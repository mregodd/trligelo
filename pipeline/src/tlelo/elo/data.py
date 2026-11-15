"""Load the match CSVs into one chronological list of games, season by season.

A game has two sides. A side is a professional Turkish club (``team`` = TFF kulupID), an
amateur club in the Turkish Cup (PGL/BAL: rated at a fixed level), or a foreign club in a
UEFA match (rated from its UEFA club coefficient). Only professional sides' ratings move.

Results used by the engine: the score after extra time when there was extra time; a
shoot-out leaves the match a draw. ``result90`` (home win / draw / away win after 90
minutes) is what the backtest predicts, as betting markets do.
"""

from __future__ import annotations

import csv
import glob
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

TIERS = {"SL": 1, "1L": 2, "2L": 3, "3L": 4}
EUROPE = ("UCL", "UEL", "UECL")
# Matches behind closed doors in Turkey (pandemic): from the decision of 12 March 2020 to
# the end of the 2020-21 season. Home advantage is measured separately for them.
CLOSED_DOORS = (date(2020, 3, 12), date(2021, 7, 31))
TURKEY = "Turkey"


@dataclass(frozen=True, slots=True)
class Side:
    kind: str  # pro | amateur | foreign
    team: int | None  # TFF kulupID for pro and amateur sides
    name: str
    coefficient: float | None = None  # foreign: UEFA club coefficient that season


@dataclass(frozen=True, slots=True)
class Game:
    key: str  # "SL:123456" (TFF macId) or "UEL:2025331" / "UEL:2018-08-09:<club>"
    season: str
    date: date
    time: str
    competition: str  # SL 1L 2L 3L TK SK UCL UEL UECL
    stage: str  # league | playoff | cup | europe
    round: str | None
    home: Side
    away: Side
    goals: tuple[int, int]  # after extra time if played (used for S and G)
    pens: tuple[int, int] | None  # shoot-out, only to know who won a final
    result90: str  # H | D | A after 90 minutes
    neutral: bool
    home_is_tr_venue: bool  # Europe: the match was played in Turkey (de facto home)
    closed: bool  # behind closed doors
    goals90: tuple[int, int] | None = None  # after 90 minutes, when extra time was played

    @property
    def score(self) -> float:
        h, a = self.goals
        return 1.0 if h > a else 0.0 if h < a else 0.5

    def winner(self) -> Side | None:
        """Who went through: after extra time, then penalties."""
        h, a = self.goals
        if h == a and self.pens:
            h, a = self.pens
        return self.home if h > a else self.away if a > h else None


@dataclass(slots=True)
class Dataset:
    seasons: list[str]
    games: dict[str, list[Game]]  # season -> games in order
    tiers: dict[str, dict[int, int]]  # season -> team -> tier (1 = Süper Lig)
    names: dict[int, str] = field(default_factory=dict)  # latest name per team
    champions: dict[str, int] = field(default_factory=dict)  # finished season -> SL champion


def _pens(row: dict) -> tuple[int, int] | None:
    return (int(row["pen_home"]), int(row["pen_away"])) if row["pen_home"] else None


def _result(h: int, a: int) -> str:
    return "H" if h > a else "A" if h < a else "D"


def _closed(d: date) -> bool:
    return CLOSED_DOORS[0] <= d <= CLOSED_DOORS[1]


def load_tiers(path: Path) -> dict[str, dict[int, int]]:
    tiers: dict[str, dict[int, int]] = defaultdict(dict)
    with path.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            tiers[r["season"]][int(r["team_id"])] = TIERS[r["competition"]]
    return dict(tiers)


def _domestic(row: dict, tiers: dict[int, int]) -> Game | None:
    if row["status"] != "played":
        return None  # forfeits are not results on the pitch; unplayed has no result
    hg, ag = int(row["home_goals"]), int(row["away_goals"])
    final = (int(row["et_home"]), int(row["et_away"])) if row["et_home"] else (hg, ag)
    sides = []
    for prefix in ("home", "away"):
        team = int(row[f"{prefix}_id"])
        kind = "pro" if team in tiers else "amateur"
        sides.append(Side(kind, team, row[f"{prefix}_name"]))
    if sides[0].kind == sides[1].kind == "amateur":
        return None  # amateur v amateur (early cup rounds): nothing to rate
    comp = row["competition"]
    rnd = row["round"] or None
    neutral = comp == "SK" or (rnd or "").startswith("Final")
    d = date.fromisoformat(row["date"])
    return Game(
        key=f"{comp}:{row['match_id']}",
        season=row["season"],
        date=d,
        time=row["time"] or "",
        competition=comp,
        stage=row["stage"],
        round=rnd,
        home=sides[0],
        away=sides[1],
        goals=final,
        pens=_pens(row),
        result90=_result(hg, ag),
        neutral=neutral,
        home_is_tr_venue=False,
        closed=_closed(d),
        goals90=(hg, ag) if row["et_home"] else None,
    )


def venue_country(venue: str) -> str | None:
    """Wikipedia names the country only for a match played outside the home club's country."""
    parts = [p.strip() for p in (venue or "").split(",")]
    return parts[-1] if len(parts) >= 3 else None


def _europe(row: dict) -> Game | None:
    if row["status"] != "played" or not row["team_id"]:
        return None
    hg, ag = int(row["home_goals"]), int(row["away_goals"])
    final = (int(row["et_home"]), int(row["et_away"])) if row["et_home"] else (hg, ag)
    tr_home = row["tr_home"] == "1"
    tr = Side("pro", int(row["team_id"]), row["home_name"] if tr_home else row["away_name"])
    coef = float(row["opponent_coefficient"]) if row["opponent_coefficient"] else None
    foreign = Side("foreign", None, row["away_name"] if tr_home else row["home_name"], coef)
    country = venue_country(row["venue"])
    d = date.fromisoformat(row["date"])
    ident = row["match_id"] or f"{row['date']}:{row['opponent']}"
    return Game(
        key=f"{row['competition']}:{ident}",
        season=row["season"],
        date=d,
        time=row["time"] or "",
        competition=row["competition"],
        stage="europe",
        round=row["round"] or None,
        home=tr if tr_home else foreign,
        away=foreign if tr_home else tr,
        goals=final,
        pens=_pens(row),
        result90=_result(hg, ag),
        # Played abroad: neutral, unless it was in Turkey (then the Turkish club is at home).
        neutral=(country is not None and country != TURKEY) or row["round"] == "F",
        home_is_tr_venue=country == TURKEY,
        closed=_closed(d),
        goals90=(hg, ag) if row["et_home"] else None,
    )


_COMP_ORDER = {
    c: i for i, c in enumerate(("UCL", "UEL", "UECL", "SK", "SL", "1L", "2L", "3L", "TK"))
}


def load_dataset(data_dir: Path) -> Dataset:
    tiers = load_tiers(data_dir / "team_seasons.csv")
    games: dict[str, list[Game]] = defaultdict(list)
    names: dict[int, str] = {}
    sl_rows: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(glob.glob(str(data_dir / "matches" / "*.csv"))):
        with open(path, encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                for p in ("home", "away"):
                    names[int(row[f"{p}_id"])] = row[f"{p}_name"]
                if row["competition"] == "SL" and row["stage"] == "league":
                    sl_rows[row["season"]].append(row)
                g = _domestic(row, tiers.get(row["season"], {}))
                if g:
                    games[g.season].append(g)
    europe = data_dir / "europe" / "matches.csv"
    if europe.exists():
        with europe.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                g = _europe(row)
                if g:
                    games[g.season].append(g)
    for season in games:
        games[season].sort(key=lambda g: (g.date, g.time, _COMP_ORDER[g.competition], g.key))
    seasons = sorted(set(tiers) | set(games))
    champions = {s: c for s, rows in sl_rows.items() if (c := league_champion(rows)) is not None}
    return Dataset(seasons, dict(games), tiers, names, champions)


def league_champion(rows: list[dict]) -> int | None:
    """Top of the table from official results (forfeits count); None if not finished.

    Points deductions are not in the data; no Süper Lig title in the window was decided
    by one.
    """
    if any(r["status"] == "not_played" for r in rows):
        return None
    pts: dict[int, list[int]] = defaultdict(lambda: [0, 0])  # points, goal difference
    for r in rows:
        h, a = int(r["home_id"]), int(r["away_id"])
        if r["status"] == "double_forfeit":
            pts[h][1] -= 3
            pts[a][1] -= 3
            continue
        hg, ag = int(r["home_goals"]), int(r["away_goals"])
        pts[h][0] += 3 if hg > ag else 1 if hg == ag else 0
        pts[a][0] += 3 if ag > hg else 1 if hg == ag else 0
        pts[h][1] += hg - ag
        pts[a][1] += ag - hg
    return max(pts, key=lambda t: tuple(pts[t])) if pts else None
