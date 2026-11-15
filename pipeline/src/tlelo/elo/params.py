"""Model parameters. ``Params()`` gives the starting values chosen before the backtest."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace


@dataclass(frozen=True, slots=True)
class Params:
    # Core formula (METODOLOJI §2-4)
    k: float = 20.0
    home: float = 65.0  # home advantage, Turkish domestic matches
    home_closed: float = 65.0  # behind closed doors (pandemic)
    home_europe: float | None = None  # European matches; None: fitted with a and b
    margin: bool = True  # goal-difference multiplier G
    # Competition weights W
    w_league: float = 1.0
    w_playoff: float = 1.0
    w_cup: float = 0.75
    w_cup_final: float = 1.0
    w_supercup: float = 0.75
    w_europe: float = 1.0
    w_amateur: float = 0.5  # extra factor for a cup match against an amateur club
    # New teams (METODOLOJI §5)
    provisional_games: int = 10
    provisional_factor: float = 1.5
    provisional_initial: bool = False  # also for every club in the first season
    newcomer: float = -50.0  # new club (from the amateur level): vs. 3. Lig mean, points
    amateur: float = -100.0  # fixed rating of amateur cup opponents, relative to the anchor
    return_pull: float = 0.5  # club back from the amateur level: pulled toward `newcomer`
    # Season transitions (METODOLOJI §5)
    regression: float = 0.10  # alpha: R <- R - alpha * (R - league mean)
    regression_own: float = 0.0  # target moves this share toward the club's own mean (v1.1 test)
    regression_seasons: int = 3  # end-of-season ratings that make the club's own mean
    seeds: tuple[float, float, float, float] = (1450.0, 1275.0, 1125.0, 1000.0)
    anchor: float = 1000.0  # 3. Lig mean at every season start
    promotion: tuple[float, float, float] = (30.0, 25.0, 20.0)  # SL/1L, 1L/2L, 2L/3L
    bonus_cup: float = 15.0
    bonus_supercup: float = 5.0
    bonus_champion: float = 0.0  # Süper Lig title (tested variant, off by default)
    # Europe (METODOLOJI §6): R = a + b * ln(1 + coefficient) [+ offset per competition].
    # None: fitted on the Turkish clubs' European results on every run.
    europe_a: float | None = None
    europe_b: float | None = None
    europe_competition_terms: bool = False
    europe_missing_coefficient: float = 1.0  # opponent without a coefficient

    def with_(self, **changes) -> Params:
        return replace(self, **changes)

    def as_dict(self) -> dict:
        return asdict(self)


def scaled_seeds(gap_scale: float, base: Params | None = None) -> tuple[float, ...]:
    """Seeds with the gaps between tiers multiplied by ``gap_scale`` (3. Lig fixed)."""
    s = (base or Params()).seeds
    bottom = s[-1]
    return tuple(bottom + (x - bottom) * gap_scale for x in s)


MODEL_VERSION = "v1.0"

# Model v1.0 (docs/backtest.md). The starting values, except where the backtest showed a
# gain in the same direction on the tuning and the holdout seasons, or the data measured
# the value directly. Every change from Params(), with the holdout log-loss cost of
# putting the starting value back (the "Plandan sapan" table of docs/backtest.md):
V1 = Params(
    k=24.0,  # 20 -> 24: +0.0008 ± 0.0003
    home_closed=50.0,  # measured: home side's mean score 0.566 closed vs 0.582 with crowds
    regression=0.3,  # 0.10 -> 0.30: +0.0008 ± 0.0005
    seeds=(1360.0, 1220.0, 1100.0, 1000.0),  # tier gaps x0.8: +0.0003 ± 0.0002
    newcomer=50.0,  # new clubs start above, not below, the 3. Lig mean: +0.0042 ± 0.0013
    return_pull=1.0,  # back from the amateur level = a new club: +0.0014 ± 0.0005
    amateur=0.0,  # amateur cup opponents play at about the 3. Lig level: +0.0001 ± 0.0001
    w_amateur=1.5,  # ... and those games are informative: +0.0002 ± 0.0002
)
