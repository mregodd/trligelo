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
    """(next round per league group, dated cup ties after ``last_match``), without clubs in
    ``skip`` (withdrawn: their matches will be forfeits)."""
    league: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        if r["competition"] in LEAGUES and r["stage"] == "league" and r["week"]:
            league[(r["competition"], r["group"])].append(r)
    rounds: dict[tuple[str, str], tuple[int, list[dict]]] = {}
    for key, rs in league.items():
        last = max((int(r["week"]) for r in rs if r["status"] in DONE), default=0)
        ahead = [r for r in rs if r["status"] == "not_played" and int(r["week"]) > last]
        if not ahead:
            continue
        week = min(int(r["week"]) for r in ahead)
        matches = [r for r in ahead if int(r["week"]) == week and not _involves(r, skip)]
        rounds[key] = (week, sorted(matches, key=lambda r: (r["date"] or "9", r["time"])))
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
