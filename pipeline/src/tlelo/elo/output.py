"""Write a run's ratings: current table and the full per-club history.

``ratings/current.csv``  one row per club of the running season, best first.
``ratings/history.csv``  every change of every club's rating, in order: matches and
                         adjustments (promotion, regression, bonuses, anchor shift). The
                         history of one club, read top to bottom, explains its rating.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date
from pathlib import Path

from tlelo.elo.data import Dataset
from tlelo.elo.engine import RunResult
from tlelo.elo.params import MODEL_VERSION

LEAGUES = {1: "SL", 2: "1L", 3: "2L", 4: "3L"}
HISTORY_COLUMNS = [
    "date", "season", "team_id", "team", "event", "competition", "round", "venue",
    "opponent", "goals_for", "goals_against", "expected", "weight", "rating_before",
    "delta", "rating_after",
]  # fmt: skip


def _write(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: "" if v is None else v for k, v in row.items()})


def history_rows(res: RunResult, data: Dataset) -> list[dict]:
    rows: list[tuple[tuple, dict]] = []
    for i, rec in enumerate(res.records):
        g = rec.game
        for is_home in (True, False):
            side, other = (g.home, g.away) if is_home else (g.away, g.home)
            if side.kind != "pro":
                continue
            delta = rec.delta_home if is_home else rec.delta_away
            before = rec.r_home if is_home else rec.r_away
            gf, ga = g.goals if is_home else g.goals[::-1]
            venue = "neutral" if rec.h == 0 else ("home" if (rec.h > 0) == is_home else "away")
            rows.append(((g.date, 1, i), {
                "date": g.date.isoformat(), "season": g.season, "team_id": side.team,
                "team": data.names.get(side.team, side.name), "event": "match",
                "competition": g.competition, "round": g.round, "venue": venue,
                "opponent": other.name, "goals_for": gf, "goals_against": ga,
                "expected": round(rec.expected if is_home else 1 - rec.expected, 4),
                "weight": rec.weight, "rating_before": round(before, 1),
                "delta": round(delta, 2), "rating_after": round(before + delta, 1),
            }))  # fmt: skip
    for j, adj in enumerate(res.adjustments):
        when = adj.date or date(int(adj.season[:4]), 7, 1)
        order = 2 if adj.date else 0  # bonuses after the final; transitions first
        rows.append(((when, order, j), {
            "date": when.isoformat(), "season": adj.season, "team_id": adj.team,
            "team": data.names.get(adj.team, ""), "event": adj.kind,
            "rating_before": round(adj.rating - adj.delta, 1), "delta": round(adj.delta, 2),
            "rating_after": round(adj.rating, 1),
        }))  # fmt: skip
    rows.sort(key=lambda r: r[0])
    return [r for _, r in rows]


def current_rows(res: RunResult, data: Dataset) -> list[dict]:
    season = data.seasons[-1]
    tiers = data.tiers[season]
    games = Counter()
    last: dict[int, str] = {}
    for rec in res.records:
        for side in (rec.game.home, rec.game.away):
            if side.kind == "pro":
                games[side.team] += 1
                last[side.team] = rec.game.date.isoformat()
    ranked = sorted(tiers, key=lambda t: -res.ratings[t])
    return [
        {
            "rank": i, "team_id": t, "team": data.names.get(t, ""),
            "league": LEAGUES[tiers[t]], "rating": round(res.ratings[t], 1),
            "games": games[t], "last_match": last.get(t), "model": MODEL_VERSION,
        }
        for i, t in enumerate(ranked, start=1)
    ]  # fmt: skip


def write_ratings(out_dir: Path, res: RunResult, data: Dataset) -> tuple[int, int]:
    current = current_rows(res, data)
    history = history_rows(res, data)
    _write(out_dir / "current.csv", list(current[0]), current)
    _write(out_dir / "history.csv", HISTORY_COLUMNS, history)
    return len(current), len(history)
