"""Turn cached tff.org pages into normalized match records (offline)."""

from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from tlelo.http import MissingPage, PoliteClient
from tlelo.tff.crawl import (
    DETAIL_PAGE,
    FORFEIT_SCORES,
    CompetitionPage,
    GroupTable,
    load_tables,
    week_params,
    weeks_to_read,
)
from tlelo.tff.parse import (
    CupRow,
    DatedRow,
    FixtureRow,
    StandingRow,
    parse_cup_rows,
    parse_match_detail,
    parse_standings,
    parse_week_dates,
)

log = logging.getLogger(__name__)


@dataclass(slots=True)
class Match:
    match_id: int
    season: str
    competition: str  # SL, 1L, 2L, 3L, TK
    stage: str  # league | playoff | cup
    round: str | None  # cup / play-off round as printed by TFF ("Yarı Final")
    group: str | None  # group label ("Beyaz", "01", "A")
    week: int | None
    date: date | None
    time: str | None
    home_id: int
    home_name: str
    away_id: int
    away_name: str
    home_goals: int | None  # regular time
    away_goals: int | None
    et_home: int | None = None  # after extra time
    et_away: int | None = None
    pen_home: int | None = None
    pen_away: int | None = None
    status: str = "played"  # played | forfeit | double_forfeit | not_played
    venue_id: int | None = None
    venue: str | None = None

    @property
    def regular_score(self) -> tuple[int | None, int | None]:
        return (self.home_goals, self.away_goals)


@dataclass(slots=True)
class CompetitionData:
    comp: CompetitionPage
    matches: list[Match]
    standings: dict[str | None, list[StandingRow]] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)


def _round_name(text: str) -> str:
    return re.sub(r"\s*Maçları\s*$", "", text).strip()


def _from_fixture(comp: CompetitionPage, table: GroupTable, r: FixtureRow, d: DatedRow | None):
    return Match(
        match_id=r.match_id,
        season=comp.season,
        competition=comp.competition,
        stage="league",
        round=None,
        group=table.label,
        week=r.week or None,
        date=d.date if d else None,
        time=d.time if d else None,
        home_id=r.home_id,
        home_name=r.home_name,
        away_id=r.away_id,
        away_name=r.away_name,
        home_goals=r.score[0] if r.score else None,
        away_goals=r.score[1] if r.score else None,
        status="played" if r.score else "not_played",
    )


def _from_cup_row(comp: CompetitionPage, c: CupRow) -> Match:
    return Match(
        match_id=c.match_id,
        season=comp.season,
        competition=comp.competition,
        stage="playoff" if comp.is_league else "cup",
        round=_round_name(c.round),
        group=None,
        week=None,
        date=c.date,
        time=c.time,
        home_id=c.home_id,
        home_name=c.home_name,
        away_id=c.away_id,
        away_name=c.away_name,
        home_goals=c.score[0] if c.score else None,
        away_goals=c.score[1] if c.score else None,
        et_home=c.extra_time[0] if c.extra_time else None,
        et_away=c.extra_time[1] if c.extra_time else None,
        pen_home=c.penalties[0] if c.penalties else None,
        pen_away=c.penalties[1] if c.penalties else None,
        status="played" if c.score else "not_played",
    )


def _from_week_row(comp: CompetitionPage, table: GroupTable, week: int, d: DatedRow):
    return Match(
        match_id=d.match_id,
        season=comp.season,
        competition=comp.competition,
        stage="league" if comp.is_league else "cup",
        round=None if comp.is_league else "Grup",
        group=table.label,
        week=week,
        date=d.date,
        time=d.time,
        home_id=d.home_id,
        home_name=d.home_name,
        away_id=d.away_id,
        away_name=d.away_name,
        home_goals=d.score[0] if d.score else None,
        away_goals=d.score[1] if d.score else None,
        status="played" if d.score else "not_played",
    )


def collect_competition(
    client: PoliteClient, comp: CompetitionPage, *, with_details: bool = True
) -> CompetitionData:
    """Build match records for one competition-season from the cache.

    ``client`` should be offline; missing week or detail pages are reported as issues
    rather than raising, so a partially downloaded season can still be inspected.
    """
    main, tables = load_tables(client, comp)
    data = CompetitionData(comp, [])
    matches: dict[int, Match] = {}

    # Knock-out rows first: cup rounds, and league play-offs.
    for html in {main, *(t.html for t in tables)}:
        for c in parse_cup_rows(html):
            matches.setdefault(c.match_id, _from_cup_row(comp, c))

    for table in tables:
        if comp.is_league:
            data.standings[table.label] = parse_standings(table.html)
        week_rows: dict[int, tuple[int, DatedRow]] = {}
        for week in weeks_to_read(comp, table):
            try:
                html = client.get(week_params(comp.page_id, table.group_id, week))
            except MissingPage:
                data.issues.append(f"week view missing: group={table.label} week={week}")
                continue
            for mid, row in parse_week_dates(html).items():
                week_rows[mid] = (week, row)

        if table.rows:  # league: fixture list + dates from the week views
            for r in table.rows:
                prev = matches.get(r.match_id)
                if prev is not None and prev.stage == "league":
                    data.issues.append(
                        f"match {r.match_id} listed in groups {prev.group} and {table.label}"
                    )
                    continue
                dated = week_rows.get(r.match_id, (None, None))[1]
                if r.score is not None and dated is None:
                    data.issues.append(f"no date for match {r.match_id} (week {r.week})")
                matches[r.match_id] = _from_fixture(comp, table, r, dated)
        else:  # no fixture list for this group: the week views are the only source
            for mid, (week, row) in week_rows.items():
                matches.setdefault(mid, _from_week_row(comp, table, week, row))

    if with_details:
        for m in matches.values():
            _apply_detail(client, m, data)

    data.matches = sorted(matches.values(), key=lambda m: (m.date or date.max, m.match_id))
    return data


def needs_detail(comp: CompetitionPage, m: Match) -> bool:
    """Possible forfeits, league play-offs and cup finals (for the venue)."""
    if m.regular_score in FORFEIT_SCORES:
        return True
    return m.stage == "playoff" or (m.stage == "cup" and (m.round or "").startswith("Final"))


def _apply_detail(client: PoliteClient, m: Match, data: CompetitionData) -> None:
    params = {"pageID": DETAIL_PAGE, "macId": m.match_id}
    if not client.is_cached(params):
        if m.regular_score in FORFEIT_SCORES:
            data.issues.append(f"3-0 not verified (no detail page): match {m.match_id}")
        return
    detail = parse_match_detail(m.match_id, client.get(params))
    m.venue_id, m.venue = detail.venue_id, detail.venue
    if m.regular_score in FORFEIT_SCORES and not detail.has_officials:
        m.status = "forfeit"


STATUSES = ("played", "forfeit", "double_forfeit", "not_played")


@dataclass(frozen=True, slots=True)
class Override:
    """A hand-checked result for a match whose fixture entry is incomplete.

    TFF leaves some matches decided by the disciplinary board without a score in the
    fixture list while its standings count them (``double_forfeit``: both sides lose 0-3).
    """

    match_id: int
    status: str
    home_goals: int | None
    away_goals: int | None


def load_overrides(path: Path) -> dict[int, Override]:
    if not path.exists():
        return {}
    out = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["status"] not in STATUSES:
                raise ValueError(f"{path.name}: bad status {r['status']!r} for {r['match_id']}")
            goals = [int(r[k]) if r[k] else None for k in ("home_goals", "away_goals")]
            out[int(r["match_id"])] = Override(int(r["match_id"]), r["status"], *goals)
    return out


def apply_overrides(data: CompetitionData, overrides: dict[int, Override]) -> None:
    for m in data.matches:
        if (o := overrides.get(m.match_id)) is not None:
            m.status, m.home_goals, m.away_goals = o.status, o.home_goals, o.away_goals


def fetch_details(client: PoliteClient, comp: CompetitionPage) -> None:
    """Second download pass: detail pages for the matches selected by ``needs_detail``."""
    offline = PoliteClient(client.cache_dir, offline=True)
    try:
        data = collect_competition(offline, comp, with_details=False)
    except MissingPage:
        log.warning("%s: season pages not cached yet, run fetch first", comp.label())
        return
    finally:
        offline.close()
    wanted = sorted(m.match_id for m in data.matches if needs_detail(comp, m))
    for match_id in wanted:
        client.get({"pageID": DETAIL_PAGE, "macId": match_id})
    log.info("%s: %d detail pages, %s", comp.label(), len(wanted), dict(client.stats))
