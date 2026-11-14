"""Backtest (docs/METODOLOJI.md §8): how well do pre-match ratings predict results?

Every game is predicted from ratings before it (the engine records them), so nothing
leaks from the future. The outcome predicted is home win / draw / away win after 90
minutes, through an ordered logistic model on the rating difference.

Seasons: 2016-17 .. 2020-21 are warm-up (ratings settling, METODOLOJI §7) and never scored.
Parameters are tuned on ``TUNE`` and checked on ``HOLDOUT``, which the tuning never sees.
The main score is the log-loss of domestic games between two professional clubs.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from tlelo.elo.data import Dataset
from tlelo.elo.engine import RunResult
from tlelo.elo.fit import OUTCOME, OrderedLogit, brier, log_loss, run_model
from tlelo.elo.params import Params, scaled_seeds

log = logging.getLogger(__name__)

TUNE = ("2021-22", "2022-23", "2023-24")
HOLDOUT = ("2024-25", "2025-26", "2026-27")


def domestic(rec) -> bool:
    g = rec.game
    return g.stage != "europe" and g.home.kind == g.away.kind == "pro"


def arrays(res: RunResult, seasons, keep: Callable = domestic):
    recs = [r for r in res.records if r.game.season in seasons and keep(r)]
    diff = np.array([r.diff for r in recs])
    y = np.array([OUTCOME[r.game.result90] for r in recs])
    return diff, y, recs


@dataclass(frozen=True, slots=True)
class Score:
    log_loss: float
    brier: float
    n: int


def score(res: RunResult, seasons=TUNE, keep: Callable = domestic, model=None) -> Score:
    """Log-loss and Brier; the ordered logit is fitted on the same games unless given."""
    diff, y, _ = arrays(res, seasons, keep)
    m = model or OrderedLogit.fit(diff, y)
    p = m.probabilities(diff)
    return Score(log_loss(p, y), brier(p, y), len(y))


def holdout_score(res: RunResult, keep: Callable = domestic) -> Score:
    """Ordered logit fitted on the tuning seasons, applied unchanged to the holdout."""
    diff, y, _ = arrays(res, TUNE, keep)
    return score(res, HOLDOUT, keep, model=OrderedLogit.fit(diff, y))


def base_rates(res: RunResult, keep: Callable = domestic) -> tuple[Score, Score]:
    """Baseline: the tuning seasons' home / draw / away frequencies for every game."""
    _, y_tune, _ = arrays(res, TUNE, keep)
    freq = np.bincount(y_tune, minlength=3) / len(y_tune)
    out = []
    for seasons in (TUNE, HOLDOUT):
        _, y, _ = arrays(res, seasons, keep)
        p = np.tile(freq, (len(y), 1))
        out.append(Score(log_loss(p, y), brier(p, y), len(y)))
    return out[0], out[1]


def tier_only(data: Dataset, res: RunResult, keep: Callable = domestic) -> tuple[Score, Score]:
    """Baseline: league level only (difference in tier, plus home advantage)."""

    def tdiff(recs):
        out = []
        for r in recs:
            t = data.tiers[r.game.season]
            out.append(150.0 * (t[r.game.away.team] - t[r.game.home.team]) + r.h)
        return np.array(out)

    _, y_tune, recs_tune = arrays(res, TUNE, keep)
    m = OrderedLogit.fit(tdiff(recs_tune), y_tune)
    scores = []
    for seasons in (TUNE, HOLDOUT):
        _, y, recs = arrays(res, seasons, keep)
        p = m.probabilities(tdiff(recs))
        scores.append(Score(log_loss(p, y), brier(p, y), len(y)))
    return scores[0], scores[1]


# --- parameter search -------------------------------------------------------------------

# name -> candidate values; "seed_scale" / "promotion_scale" scale the default tuples.
GRID: dict[str, list] = {
    "k": [16, 20, 24, 28, 32, 36, 40],
    "home": [40, 65, 85, 105, 125, 150],
    "home_closed": [0, 20, 40, 65],
    "margin": [True, False],
    "regression": [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40],
    "seed_scale": [0.2, 0.4, 0.6, 0.8, 1.0, 1.25],
    "promotion_scale": [0.0, 0.5, 1.0, 2.0],
    "w_cup": [0.5, 0.75, 1.0],
    "w_cup_final": [0.75, 1.0, 1.5],
    "w_supercup": [0.5, 0.75, 1.0, 1.5],
    "w_playoff": [0.5, 0.75, 1.0, 1.25],
    "w_europe": [0.0, 0.25, 0.5, 0.75, 1.0],
    "w_amateur": [0.25, 0.5, 1.0, 1.5],
    "amateur": [-200.0, -150.0, -100.0, -50.0, 0.0],
    "provisional_games": [5, 10, 20],
    "provisional_factor": [1.0, 1.5, 2.0],
    "provisional_initial": [False, True],
    "newcomer": [-100.0, -50.0, 0.0, 50.0, 100.0],
    "return_pull": [0.0, 0.5, 1.0],
    "bonus_cup": [0.0, 15.0, 30.0],
    "bonus_champion": [0.0, 15.0, 30.0, 45.0, 60.0, 90.0],
}
# Europe-only choices (home advantage, competition offsets) are fitted on the European
# matches themselves, not chosen by domestic prediction: see ``fit.fit_europe``.


def apply(params: Params, name: str, value) -> Params:
    if name == "seed_scale":
        return params.with_(seeds=scaled_seeds(value))
    if name == "promotion_scale":
        return params.with_(promotion=tuple(x * value for x in Params().promotion))
    return params.with_(**{name: value})


def current_value(params: Params, name: str):
    if name == "seed_scale":
        base = Params().seeds
        return round((params.seeds[0] - base[-1]) / (base[0] - base[-1]), 4)
    if name == "promotion_scale":
        return round(params.promotion[0] / Params().promotion[0], 4)
    return getattr(params, name)


@dataclass(slots=True)
class SearchStep:
    name: str
    value: object
    log_loss: float


def coordinate_search(data: Dataset, start: Params, passes: int = 2):
    """Change one parameter at a time to its best grid value; repeat ``passes`` times."""
    cache: dict[Params, float] = {}

    def objective(p: Params) -> float:
        if p not in cache:
            cache[p] = score(run_model(data, p)).log_loss
        return cache[p]

    best, best_ll = start, objective(start)
    steps: list[SearchStep] = []
    sensitivity: dict[str, dict] = {}
    for n in range(passes):
        changed = False
        for name, values in GRID.items():
            results = {v: objective(apply(best, name, v)) for v in values}
            sensitivity[name] = results
            v_best = min(results, key=results.get)
            if results[v_best] < best_ll - 1e-6:
                best, best_ll, changed = apply(best, name, v_best), results[v_best], True
                steps.append(SearchStep(name, v_best, best_ll))
            log.info(
                "pass %d %-26s best=%s ll=%.5f", n + 1, name, current_value(best, name), best_ll
            )
        if not changed:
            break
    return best, steps, sensitivity, len(cache)


def europe_residuals(res: RunResult, seasons) -> dict[str, tuple[int, float]]:
    """Mean (S − E) of the Turkish side per competition: > 0 means better than expected."""
    out: dict[str, list[float]] = {}
    for r in res.records:
        g = r.game
        if g.stage != "europe" or g.season not in seasons:
            continue
        tr_home = g.home.kind == "pro"
        e = r.expected if tr_home else 1 - r.expected
        s = g.score if tr_home else 1 - g.score
        out.setdefault(g.competition, []).append(s - e)
    return {k: (len(v), float(np.mean(v))) for k, v in sorted(out.items())}


def implied_gap(res: RunResult, seasons=TUNE) -> dict[tuple[int, int], tuple[int, float, float]]:
    """Cup games between clubs of different tiers: games, upper tier's mean score, and the
    rating gap ``400·log10(p / (1 − p))`` that score implies."""
    acc: dict[tuple[int, int], list[float]] = {}
    for r in res.records:
        g = r.game
        if g.competition != "TK" or g.season not in seasons or not domestic(r):
            continue
        t = res.tiers[g.season]
        th, ta = t[g.home.team], t[g.away.team]
        if th == ta:
            continue
        upper_home = th < ta
        s = g.score if upper_home else 1 - g.score
        acc.setdefault((min(th, ta), max(th, ta)), []).append(s)
    out = {}
    for key, v in sorted(acc.items()):
        p = min(max(float(np.mean(v)), 1e-3), 1 - 1e-3)
        out[key] = (len(v), p, 400 * math.log10(p / (1 - p)))
    return out
