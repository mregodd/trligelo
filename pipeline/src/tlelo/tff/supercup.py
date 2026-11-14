"""Turkcell Süper Kupa.

TFF has no season pages for the Süper Kupa, only a history table of finals on the
competition page. Each final links to its match detail page, which gives the club ids,
regular-time score, date and venue. Penalty shoot-outs ("(4-2 P.)") and forfeits
("(HÜKMEN)") are read from the history table.

Since 2025-26 the Süper Kupa is a four-team event with semi-finals. Those matches are not
in the history table and their TFF match ids could not be found, so they are entered by
hand, with their source, in ``data/sources/supercup_extra.csv`` (negative match ids).
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from tlelo.http import PoliteClient
from tlelo.tff.collect import CompetitionData, Match
from tlelo.tff.crawl import DETAIL_PAGE, CompetitionPage
from tlelo.tff.parse import clean_text, parse_match_detail

SUPERCUP_PAGE = 329
FIRST_DATE = date(2016, 7, 1)  # start of the 2016-17 season

_ROW_SPLIT = re.compile(r"<tr\b", re.IGNORECASE)
_CELL = re.compile(r"<td\b[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)
_MATCH_ID = re.compile(r"macID=(\d+)", re.IGNORECASE)
_PENALTIES = re.compile(r"\(\s*(\d+)\s*-\s*(\d+)\s*P\.?\s*\)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class SuperCupFinal:
    match_id: int
    date: date
    venue: str
    score: tuple[int, int] | None  # regular (or extra) time, from the history table
    penalties: tuple[int, int] | None
    forfeit: bool


def season_of(d: date) -> str:
    """July-June seasons: 2017-01-10 -> "2016-17"."""
    start = d.year if d.month >= 7 else d.year - 1
    return f"{start}-{str(start + 1)[2:]}"


def parse_history(html: str) -> list[SuperCupFinal]:
    out = []
    for chunk in _ROW_SPLIT.split(html):
        mid = _MATCH_ID.search(chunk)
        cells = [clean_text(c) for c in _CELL.findall(chunk)]
        if not mid or len(cells) < 5:
            continue
        m = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{4})", cells[0])
        if not m:
            continue
        score_text = cells[3]
        pens = _PENALTIES.search(score_text)
        score = re.match(r"\s*(\d+)\s*-\s*(\d+)", score_text)
        out.append(
            SuperCupFinal(
                match_id=int(mid[1]),
                date=date(int(m[3]), int(m[2]), int(m[1])),
                venue=cells[1],
                score=(int(score[1]), int(score[2])) if score else None,
                penalties=(int(pens[1]), int(pens[2])) if pens else None,
                forfeit="HÜKMEN" in score_text.upper(),
            )
        )
    return out


def _finals(client: PoliteClient) -> list[SuperCupFinal]:
    history = parse_history(client.get({"pageID": SUPERCUP_PAGE}))
    return [f for f in history if f.date >= FIRST_DATE]


def _int(value: str) -> int | None:
    return int(value) if value.strip() else None


def load_extra(path: Path) -> list[Match]:
    """Hand-entered matches (see module docstring)."""
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["date"])
            out.append(
                Match(
                    match_id=int(r["match_id"]),
                    season=season_of(d),
                    competition="SK",
                    stage="cup",
                    round=r["round"],
                    group=None,
                    week=None,
                    date=d,
                    time=None,
                    home_id=int(r["home_id"]),
                    home_name=r["home_name"],
                    away_id=int(r["away_id"]),
                    away_name=r["away_name"],
                    home_goals=_int(r["home_goals"]),
                    away_goals=_int(r["away_goals"]),
                    pen_home=_int(r["pen_home"]),
                    pen_away=_int(r["pen_away"]),
                    venue=r["venue"] or None,
                )
            )
    return out


def fetch_supercup(client: PoliteClient, *, refresh: bool = False) -> None:
    client.get({"pageID": SUPERCUP_PAGE}, refresh=refresh)
    for final in _finals(client):
        client.get({"pageID": DETAIL_PAGE, "macId": final.match_id})


def _final_match(client: PoliteClient, final: SuperCupFinal) -> Match:
    d = parse_match_detail(
        final.match_id, client.get({"pageID": DETAIL_PAGE, "macId": final.match_id})
    )
    if d.home_id is None or d.away_id is None:
        raise ValueError(f"Süper Kupa match {final.match_id}: detail page lacks the teams")
    # Detail pages add shoot-out goals to the score (1-1, pens 0-3 is shown as 1-4), so the
    # regular score comes from the history table (same team order as the detail page).
    score = final.score
    if score is None and d.score is not None:
        pens = final.penalties or (0, 0)
        score = (d.score[0] - pens[0], d.score[1] - pens[1])
    return Match(
        match_id=final.match_id,
        season=season_of(final.date),
        competition="SK",
        stage="cup",
        round="Final",
        group=None,
        week=None,
        date=final.date,
        time=d.time,
        home_id=d.home_id,
        home_name=d.home_name or "",
        away_id=d.away_id,
        away_name=d.away_name or "",
        home_goals=score[0] if score else None,
        away_goals=score[1] if score else None,
        pen_home=final.penalties[0] if final.penalties else None,
        pen_away=final.penalties[1] if final.penalties else None,
        status="forfeit" if final.forfeit else "played",
        venue_id=d.venue_id,
        venue=d.venue or final.venue,
    )


def collect_supercup(client: PoliteClient, extra_csv: Path) -> list[CompetitionData]:
    """One CompetitionData per season."""
    matches = [_final_match(client, f) for f in _finals(client)] + load_extra(extra_csv)
    by_season: dict[str, CompetitionData] = {}
    for m in sorted(matches, key=lambda m: (m.date or date.max, m.match_id)):
        comp = CompetitionPage("SK", m.season, SUPERCUP_PAGE, current=False)
        by_season.setdefault(m.season, CompetitionData(comp, [])).matches.append(m)
    return list(by_season.values())
