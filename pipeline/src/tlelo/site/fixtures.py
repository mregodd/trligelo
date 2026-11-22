"""Upcoming matches for the website: each league group's next round and dated cup ties.

TFF lists the season's pairings early but gives dates only a week or two ahead, so a round
is found by its week number: the first week after the last one with a result. Matches left
over from earlier weeks (postponed, or played but not yet entered) are not part of it.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

LEAGUES = ("SL", "1L", "2L", "3L")
CUPS = ("TK", "SK")
DONE = ("played", "forfeit", "double_forfeit")


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def upcoming(rows: list[dict], last_match: date, skip: set[int]):
    """(league matches still to come by (competition, group, week), dated cup ties after
    ``last_match``), without clubs in ``skip`` (withdrawn: their matches will be forfeits).

    Per league group: the next round after the last week with a result, and any match of
    that week or an earlier one dated from ``last_match`` on (a round's Monday match, a
    postponed match with its new date). Older unplayed matches are left over."""
    league: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        if r["competition"] in LEAGUES and r["stage"] == "league" and r["week"]:
            league[(r["competition"], r["group"])].append(r)
    rounds: dict[tuple[str, str, int], list[dict]] = defaultdict(list)
    for (comp, group), rs in league.items():
        last = max((int(r["week"]) for r in rs if r["status"] in DONE), default=0)
        todo = [r for r in rs if r["status"] == "not_played"]
        nxt = min((int(r["week"]) for r in todo if int(r["week"]) > last), default=None)
        for r in todo:
            week = int(r["week"])
            due = r["date"] and date.fromisoformat(r["date"]) >= last_match
            if (week == nxt or (week <= last and due)) and not _involves(r, skip):
                rounds[(comp, group, week)].append(r)
    for matches in rounds.values():
        matches.sort(key=lambda r: (r["date"] or "9", r["time"]))
    cup = sorted(
        (r for r in rows if r["competition"] in CUPS and r["status"] == "not_played"
         and r["date"] and date.fromisoformat(r["date"]) > last_match and not _involves(r, skip)),
        key=lambda r: (r["date"], r["time"]),
    )  # fmt: skip
    return rounds, cup


def _involves(r: dict, teams: set[int]) -> bool:
    return int(r["home_id"]) in teams or int(r["away_id"]) in teams


def chances(p_away: float, p_draw: float, p_home: float) -> list[int]:
    """Home win, draw, away win in whole percent adding up to 100."""
    home, away = round(p_home * 100), round(p_away * 100)
    return [home, 100 - home - away, away]


def stakes(k: float, w: float, e: float) -> list[float]:
    """Rating change for a win, draw, loss by one goal, for the side whose expected score is
    ``e`` (a bigger margin multiplies it, see METODOLOJI §4)."""
    return [round(k * w * (s - e), 1) + 0.0 for s in (1.0, 0.5, 0.0)]
