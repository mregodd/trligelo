"""Download the tff.org pages needed for each competition-season into the cache.

``fetch_competition`` gets the season page, one page per group, and one week view per
played week plus the coming one (week views are the only place that shows kick-off dates).
Match detail pages are a second pass, see ``tlelo.tff.collect.fetch_details``.
"""

from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from pathlib import Path

from tlelo.http import PoliteClient
from tlelo.tff.parse import (
    FixtureRow,
    parse_fixture,
    parse_groups,
    parse_standings,
    parse_week_dates,
    parse_week_links,
    rows_for_group,
)

log = logging.getLogger(__name__)

LEAGUES = ("SL", "1L", "2L", "3L")
FORFEIT_SCORES = {(3, 0), (0, 3)}
DETAIL_PAGE = 29


@dataclass(frozen=True, slots=True)
class CompetitionPage:
    competition: str  # SL, 1L, 2L, 3L, TK
    season: str  # "2016-17"
    page_id: int
    current: bool  # live page of the running season (content still changes)

    @property
    def is_league(self) -> bool:
        return self.competition in LEAGUES

    def label(self) -> str:
        return f"{self.competition} {self.season}"


@dataclass(frozen=True, slots=True)
class GroupTable:
    group_id: int | None
    label: str | None
    html: str
    rows: list[FixtureRow]


def load_pages(path: Path) -> list[CompetitionPage]:
    with path.open(encoding="utf-8", newline="") as fh:
        return [
            CompetitionPage(r["competition"], r["season"], int(r["page_id"]), r["current"] == "1")
            for r in csv.DictReader(fh)
        ]


def week_params(page_id: int, group_id: int | None, week: int) -> dict[str, int]:
    params = {"pageID": page_id}
    if group_id is not None:
        params["grupID"] = group_id
    params["hafta"] = week
    return params


def load_tables(client: PoliteClient, comp: CompetitionPage, *, refresh: bool = False):
    """Return (main page HTML, group tables). Ungrouped pages yield one table."""
    main = client.get({"pageID": comp.page_id}, refresh=refresh)
    groups = parse_groups(main)
    if not groups:
        return main, [GroupTable(None, None, main, parse_fixture(main))]
    tables = []
    for gid, label in groups.items():
        html = client.get({"pageID": comp.page_id, "grupID": gid}, refresh=refresh)
        teams = {s.team_id for s in parse_standings(html)}
        rows = rows_for_group(parse_fixture(html), label, teams)
        tables.append(GroupTable(gid, label, html, rows))
    return main, tables


def played_weeks(rows: list[FixtureRow]) -> list[int]:
    return sorted({r.week for r in rows if r.score is not None and r.week > 0})


def weeks_to_read(comp: CompetitionPage, table: GroupTable) -> list[int]:
    """Week views needed for a table.

    With a fixture list: every week with a played match and, in the running season, the
    coming week, whose view carries the kick-off dates TFF has set so far. Without one (cup
    group stages, and league groups whose fixture list TFF does not show), the group's
    matches only exist on the week views linked from the group page.
    """
    if table.rows:
        played = played_weeks(table.rows)
        coming = played[-1] + 1 if played else min(r.week for r in table.rows)
        if comp.current and any(r.week == coming for r in table.rows):
            return [*played, coming]
        return played
    if table.group_id is not None:
        return parse_week_links(table.html)
    return []


def fetch_competition(
    client: PoliteClient, comp: CompetitionPage, *, refresh_current: bool = False
) -> None:
    refresh = comp.current and refresh_current
    _, tables = load_tables(client, comp, refresh=refresh)
    for table in tables:
        played = set(played_weeks(table.rows))
        for week in weeks_to_read(comp, table):
            params = week_params(comp.page_id, table.group_id, week)
            # The coming week's view changes until it is played: TFF sets the dates in stages.
            stale = refresh and (
                not table.rows
                or week not in played
                or _week_is_stale(client, params, table.rows, week)
            )
            client.get(params, refresh=stale)
    log.info("%s: %s", comp.label(), dict(client.stats))


def _week_is_stale(
    client: PoliteClient, params: dict[str, int], rows: list[FixtureRow], week: int
) -> bool:
    """A cached week view is stale if a match now played has no score on it yet."""
    if not client.is_cached(params):
        return False  # not cached: get() downloads it anyway
    dated = parse_week_dates(client.get(params))
    return any(
        r.match_id not in dated or dated[r.match_id].score is None
        for r in rows
        if r.week == week and r.score is not None
    )
