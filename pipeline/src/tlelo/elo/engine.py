"""The Elo engine (docs/METODOLOJI.md): one deterministic pass over every season.

Per season:
  1. transition from the previous season: promotion/relegation adjustment (P), Süper Lig
     title bonus (variant), new and returning clubs, regression to the league mean,
     shift of the whole scale so that the 3. Lig mean is ``anchor``;
  2. games in date order; cup bonuses (B) right after the final.

Only professional Turkish clubs have ratings that move. Amateur cup opponents sit at a
fixed level below the anchor; foreign clubs are rated from their UEFA club coefficient.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from tlelo.elo.data import Dataset, Game, Side
from tlelo.elo.params import Params


def expected(diff: float) -> float:
    """Expected score of the side ``diff`` points ahead (home advantage included)."""
    return 1.0 / (1.0 + 10.0 ** (-diff / 400.0))


def margin_factor(goal_diff: int) -> float:
    """G (eloratings.net): 1 goal -> 1, 2 -> 1.5, N >= 3 -> (11 + N) / 8."""
    n = abs(goal_diff)
    if n <= 1:
        return 1.0
    if n == 2:
        return 1.5
    return (11 + n) / 8


@dataclass(frozen=True, slots=True)
class EuropeModel:
    """Foreign club rating ``a + b * ln(1 + coefficient) + offsets[competition]``, and the
    home advantage in European matches (fitted together, see ``tlelo.elo.fit``)."""

    a: float
    b: float
    home: float
    offsets: tuple[tuple[str, float], ...] = ()

    def rating(self, coefficient: float, competition: str) -> float:
        return self.a + self.b * math.log1p(coefficient) + dict(self.offsets).get(competition, 0.0)


@dataclass(slots=True)
class GameRecord:
    game: Game
    r_home: float  # ratings before the game (a fixed side's level for amateur / foreign)
    r_away: float
    h: float  # home advantage given to the home side (0 on neutral ground)
    expected: float  # home side's expected score
    weight: float  # W
    delta_home: float  # rating change of each side (0 for a fixed side)
    delta_away: float
    k_home: float = 0.0  # K used for each side (provisional factor included)
    k_away: float = 0.0
    margin: float = 1.0  # G
    seq: int = 0  # processing order across games and adjustments

    @property
    def diff(self) -> float:
        return self.r_home + self.h - self.r_away


@dataclass(slots=True)
class Adjustment:
    season: str
    team: int
    kind: str  # seed | newcomer | return | promotion | relegation | regression | anchor |
    #            cup | supercup | champion
    delta: float
    rating: float  # after the adjustment
    date: date | None = None  # cup bonuses: the final; season transitions: None
    seq: int = 0  # processing order across games and adjustments


@dataclass(slots=True)
class RunResult:
    params: Params
    records: list[GameRecord]
    adjustments: list[Adjustment]
    ratings: dict[int, float]
    europe: EuropeModel
    tiers: dict[str, dict[int, int]] = field(default_factory=dict)


class Engine:
    def __init__(self, data: Dataset, params: Params, europe: EuropeModel):
        self.data = data
        self.p = params
        self.europe = europe
        self.r: dict[int, float] = {}
        self.played: dict[int, int] = defaultdict(int)
        self.provisional: set[int] = set()
        self.records: list[GameRecord] = []
        self.adjustments: list[Adjustment] = []
        self._seq = 0

    def _next(self) -> int:
        self._seq += 1
        return self._seq

    # --- ratings of the two kinds of fixed sides ---------------------------------------

    def foreign_rating(self, side: Side, competition: str) -> float:
        coef = side.coefficient
        if coef is None:
            coef = self.p.europe_missing_coefficient
        return self.europe.rating(coef, competition)

    def rating(self, side: Side, game: Game) -> float:
        if side.kind == "pro":
            return self.r[side.team]
        if side.kind == "amateur":
            return self.p.anchor + self.p.amateur
        return self.foreign_rating(side, game.competition)

    # --- one game ----------------------------------------------------------------------

    def weight(self, g: Game) -> float:
        p = self.p
        if g.stage == "europe":
            w = p.w_europe
        elif g.competition == "SK":
            w = p.w_supercup
        elif g.competition == "TK":
            w = p.w_cup_final if (g.round or "").startswith("Final") else p.w_cup
        elif g.stage == "playoff":
            w = p.w_playoff
        else:
            w = p.w_league
        if "amateur" in (g.home.kind, g.away.kind):
            w *= p.w_amateur
        return w

    def home_advantage(self, g: Game) -> float:
        if g.home_is_tr_venue:  # Europe, played in Turkey: the Turkish club is at home
            h = self.p.home_closed if g.closed else self.europe.home
            return h if g.home.kind == "pro" else -h
        if g.neutral:
            return 0.0
        if g.closed:
            return self.p.home_closed
        return self.europe.home if g.stage == "europe" else self.p.home

    def k_for(self, side: Side) -> float:
        k = self.p.k
        if side.team in self.provisional and self.played[side.team] < self.p.provisional_games:
            k *= self.p.provisional_factor
        return k

    def play(self, g: Game) -> None:
        rh, ra = self.rating(g.home, g), self.rating(g.away, g)
        h = self.home_advantage(g)
        e = expected(rh + h - ra)
        w = self.weight(g)
        gm = margin_factor(g.goals[0] - g.goals[1]) if self.p.margin else 1.0
        surprise = g.score - e
        kh = self.k_for(g.home) if g.home.kind == "pro" else 0.0
        ka = self.k_for(g.away) if g.away.kind == "pro" else 0.0
        dh = kh * w * gm * surprise
        da = -ka * w * gm * surprise
        for side, d in ((g.home, dh), (g.away, da)):
            if side.kind == "pro":
                self.r[side.team] += d
                self.played[side.team] += 1
        self.records.append(GameRecord(g, rh, ra, h, e, w, dh, da, kh, ka, gm, self._next()))

        if (g.round or "").startswith("Final") and g.competition in ("TK", "SK"):
            bonus = self.p.bonus_cup if g.competition == "TK" else self.p.bonus_supercup
            win = g.winner()
            if bonus and win is not None and win.kind == "pro":
                kind = "cup" if g.competition == "TK" else "supercup"
                self._adjust(g.season, win.team, kind, bonus, g.date)

    # --- season transitions --------------------------------------------------------------

    def _adjust(
        self, season: str, team: int, kind: str, delta: float, when: date | None = None
    ) -> None:
        self.r[team] += delta
        self.adjustments.append(
            Adjustment(season, team, kind, delta, self.r[team], when, self._next())
        )

    def start_season(self, season: str, previous: str | None) -> None:
        p = self.p
        tiers = self.data.tiers.get(season, {})
        if previous is None:
            for team, tier in tiers.items():
                self.r[team] = p.seeds[tier - 1]
                if p.provisional_initial:
                    self.provisional.add(team)
                self.adjustments.append(
                    Adjustment(season, team, "seed", 0.0, self.r[team], None, self._next())
                )
            return

        before = self.data.tiers.get(previous, {})
        # Promotion / relegation adjustment, one P per boundary crossed.
        for team, tier in tiers.items():
            old = before.get(team)
            if old is None or old == tier:
                continue
            lo, hi = sorted((old, tier))
            amount = sum(p.promotion[b - 1] for b in range(lo, hi))
            if amount:
                kind = "promotion" if tier < old else "relegation"
                self._adjust(season, team, kind, amount if tier < old else -amount)
        # Süper Lig title bonus (variant).
        champ = self.data.champions.get(previous)
        if p.bonus_champion and champ is not None and champ in self.r:
            self._adjust(season, champ, "champion", p.bonus_champion)
        # Regression toward the league mean among clubs continuing from last season
        # (keeps each league's total).
        continuing: dict[int, list[int]] = defaultdict(list)
        for team, tier in tiers.items():
            if team in self.r and team in before:
                continuing[tier].append(team)
        if p.regression:
            for teams in continuing.values():
                mean = sum(self.r[t] for t in teams) / len(teams)
                for t in teams:
                    self._adjust(season, t, "regression", -p.regression * (self.r[t] - mean))
        # New clubs (from the amateur level) start `newcomer` points above the mean of the
        # continuing 3. Lig clubs; clubs back from the amateur level are pulled toward it.
        bottom_now = continuing.get(4) or [t for t in self.r if t in tiers]
        entry = sum(self.r[t] for t in bottom_now) / len(bottom_now) + p.newcomer
        for team in tiers:
            if team not in self.r:
                self.r[team] = entry
                self.provisional.add(team)
                self.played[team] = 0
                self.adjustments.append(
                    Adjustment(season, team, "newcomer", 0.0, entry, None, self._next())
                )
            elif team not in before:
                self.provisional.add(team)
                self.played[team] = 0
                self._adjust(season, team, "return", p.return_pull * (entry - self.r[team]))
        # Anchor: shift every rating so the 3. Lig mean is `anchor`.
        bottom = [t for t, tier in tiers.items() if tier == 4]
        if bottom:
            shift = p.anchor - sum(self.r[t] for t in bottom) / len(bottom)
            for t in self.r:  # clubs not playing this season move too, silently
                self.r[t] += shift
                if t in tiers:
                    self.adjustments.append(
                        Adjustment(season, t, "anchor", shift, self.r[t], None, self._next())
                    )

    def run(self) -> RunResult:
        previous = None
        for season in self.data.seasons:
            self.start_season(season, previous)
            for g in self.data.games.get(season, []):
                self.play(g)
            previous = season
        return RunResult(
            self.p,
            self.records,
            self.adjustments,
            dict(self.r),
            self.europe,
            self.data.tiers,
        )
