"""Model parameters. ``Params()`` gives the starting values of docs/PLAN.md §4.3-4.7."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace


@dataclass(frozen=True, slots=True)
class Params:
    # Core formula (PLAN §4.2-4.3)
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
    # New teams (PLAN §4.3, §4.8)
    provisional_games: int = 10
    provisional_factor: float = 1.5
    provisional_initial: bool = False  # also for every club in the first season
    newcomer: float = -50.0  # new club (from the amateur level): vs. 3. Lig mean, points
    amateur: float = -100.0  # fixed rating of amateur cup opponents, relative to the anchor
    return_pull: float = 0.5  # club back from the amateur level: pulled toward `newcomer`
    # Season transitions (PLAN §4.3-4.6)
    regression: float = 0.10  # alpha: R <- R - alpha * (R - league mean)
    seeds: tuple[float, float, float, float] = (1450.0, 1275.0, 1125.0, 1000.0)
    anchor: float = 1000.0  # 3. Lig mean at every season start
    promotion: tuple[float, float, float] = (30.0, 25.0, 20.0)  # SL/1L, 1L/2L, 2L/3L
    bonus_cup: float = 15.0
    bonus_supercup: float = 5.0
    bonus_champion: float = 0.0  # Süper Lig title (tested variant, off by default)
    # Europe (PLAN §4.7): R = a + b * ln(1 + coefficient) [+ offset per competition].
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

# Model v1.0 (docs/faz-2-rapor.md). Starting values of the plan, except where the
# backtest showed a clear gain on both the tuning seasons and the holdout seasons, or the
# data measured the value directly. Every change from Params():
V1 = Params(
    k=24.0,  # 20 -> 24: holdout log-loss -0.0014 ± 0.0003
    home_closed=50.0,  # measured: home side's mean score 0.566 closed vs 0.582 with crowds
    regression=0.3,  # 0.10 -> 0.30: holdout -0.0024 ± 0.0006
    seeds=(1360.0, 1220.0, 1100.0, 1000.0),  # tier gaps x0.8: holdout -0.0004 ± 0.0002
    newcomer=50.0,  # new clubs do not start below the 3. Lig mean: holdout -0.0057 ± 0.0017
    return_pull=1.0,  # back from the amateur level = a new club: holdout -0.0014 ± 0.0005
    amateur=0.0,  # amateur cup opponents play at about the 3. Lig level
    w_amateur=1.5,  # ... and those games are informative: holdout -0.0002 ± 0.0001
)
