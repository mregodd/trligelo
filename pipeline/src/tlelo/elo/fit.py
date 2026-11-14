"""Statistical fits: the Europe opponent model and the win/draw/loss model.

Europe (PLAN §4.7): a foreign club's rating is ``a + b * ln(1 + coefficient)`` (plus an
optional offset per competition). a and b are chosen so that the Elo expected scores of
the Turkish clubs' European matches fit their results best (fractional logistic
likelihood on the Elo score S: 1 / 0.5 / 0). The Turkish ratings themselves depend on
a and b, so ``run_model`` alternates engine runs and fits until a and b settle.

Win/draw/loss (PLAN §4.9): an ordered logistic model on the rating difference,
``P(away) = σ(c1 − β·d)``, ``P(home) = 1 − σ(c2 − β·d)``, ``d`` in hundreds of points.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from tlelo.elo.data import Dataset
from tlelo.elo.engine import Engine, EuropeModel, GameRecord, RunResult
from tlelo.elo.params import Params

KAPPA = math.log(10) / 400  # Elo: E = expit(KAPPA * diff)
START = (1150.0, 150.0)  # a, b before the first fit
START_HOME = 65.0


@dataclass(frozen=True, slots=True)
class EuropeRows:
    rating: np.ndarray  # Turkish club's rating before the match
    side: np.ndarray  # +1 Turkish club at home (or the match was in Turkey), -1 away, 0 neutral
    fixed_h: np.ndarray  # home advantage not fitted here (closed doors), else 0
    open_: np.ndarray  # 1 where the fitted Europe home advantage applies
    x: np.ndarray  # ln(1 + opponent coefficient)
    competition: np.ndarray
    s: np.ndarray  # Turkish club's Elo score (after extra time; shoot-out = draw)


def europe_rows(records: list[GameRecord], home_closed: float) -> EuropeRows:
    cols: dict[str, list] = {k: [] for k in ("r", "side", "fh", "op", "x", "c", "s")}
    for rec in records:
        g = rec.game
        if g.stage != "europe":
            continue
        tr_home = g.home.kind == "pro"
        foreign = g.away if tr_home else g.home
        if g.home_is_tr_venue:
            side = 1
        elif g.neutral:
            side = 0
        else:
            side = 1 if tr_home else -1
        cols["r"].append(rec.r_home if tr_home else rec.r_away)
        cols["side"].append(side)
        cols["fh"].append(side * home_closed if g.closed else 0.0)
        cols["op"].append(0.0 if g.closed else 1.0)
        cols["x"].append(math.log1p(foreign.coefficient or 0.0))
        cols["c"].append(g.competition)
        cols["s"].append(g.score if tr_home else 1.0 - g.score)
    a = {k: np.array(v) for k, v in cols.items()}
    return EuropeRows(a["r"], a["side"], a["fh"], a["op"], a["x"], a["c"], a["s"])


def fit_europe(
    records: list[GameRecord], params: Params, start: EuropeModel
) -> tuple[EuropeModel, float, int]:
    """Maximum-likelihood a, b, home advantage (unless fixed) and competition offsets.

    Returns the model, the negative log-likelihood and the number of matches.
    """
    rows = europe_rows(records, params.home_closed)
    if len(rows.s) < 20:
        return start, float("nan"), len(rows.s)
    extra = ["UEL", "UECL"] if params.europe_competition_terms else []  # relative to UCL
    dummies = [(rows.competition == c).astype(float) for c in extra]
    fit_home = params.home_europe is None

    def unpack(theta):
        a, b, *rest = theta
        home = rest.pop(0) if fit_home else params.home_europe
        return a, b, home, rest

    def nll(theta):
        a, b, home, cs = unpack(theta)
        opp = a + b * rows.x + sum(c * d for c, d in zip(cs, dummies, strict=True))
        h = rows.side * home * rows.open_ + rows.fixed_h
        e = np.clip(expit(KAPPA * (rows.rating + h - opp)), 1e-9, 1 - 1e-9)
        return -np.sum(rows.s * np.log(e) + (1 - rows.s) * np.log(1 - e))

    theta0 = [start.a, start.b, *([start.home] if fit_home else []), *([0.0] * len(extra))]
    res = minimize(nll, np.array(theta0), method="BFGS")
    a, b, home, cs = unpack(res.x)
    offsets = tuple((c, float(v)) for c, v in zip(extra, cs, strict=True))
    return EuropeModel(float(a), float(b), float(home), offsets), float(res.fun), len(rows.s)


def run_model(data: Dataset, params: Params, *, max_rounds: int = 8, tol: float = 0.5):
    """Engine run with the Europe opponent model fitted to that run's own ratings."""
    home = params.home_europe if params.home_europe is not None else START_HOME
    if params.europe_a is not None and params.europe_b is not None:
        return Engine(data, params, EuropeModel(params.europe_a, params.europe_b, home)).run()
    europe = EuropeModel(*START, home)
    result: RunResult | None = None
    for _ in range(max_rounds):
        result = Engine(data, params, europe).run()
        fitted, _, _ = fit_europe(result.records, params, europe)
        change = max(
            abs(fitted.a - europe.a),
            abs(fitted.b - europe.b),
            abs(fitted.home - europe.home),
            *(abs(v - dict(europe.offsets).get(k, 0.0)) for k, v in fitted.offsets),
        )
        europe = fitted
        if change < tol or params.w_europe == 0:
            break
    return Engine(data, params, europe).run() if result.europe != europe else result


# --- win / draw / loss model ----------------------------------------------------------

OUTCOME = {"A": 0, "D": 1, "H": 2}


@dataclass(frozen=True, slots=True)
class OrderedLogit:
    beta: float
    c1: float
    c2: float

    def probabilities(self, diff: np.ndarray) -> np.ndarray:
        z = self.beta * diff / 100.0
        p_away = expit(self.c1 - z)
        p_home = 1.0 - expit(self.c2 - z)
        return np.column_stack([p_away, 1.0 - p_away - p_home, p_home])

    @staticmethod
    def fit(diff: np.ndarray, y: np.ndarray) -> OrderedLogit:
        def nll(theta):
            beta, c1, log_gap = theta
            m = OrderedLogit(beta, c1, c1 + math.exp(log_gap))
            p = np.clip(m.probabilities(diff)[np.arange(len(y)), y], 1e-12, 1.0)
            return -np.sum(np.log(p))

        res = minimize(
            nll,
            np.array([0.5, -1.0, 0.0]),
            method="Nelder-Mead",
            options={"xatol": 1e-5, "fatol": 1e-4, "maxiter": 2000},
        )
        beta, c1, log_gap = res.x
        return OrderedLogit(float(beta), float(c1), float(c1 + math.exp(log_gap)))


def log_loss(p: np.ndarray, y: np.ndarray) -> float:
    return float(-np.mean(np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1.0))))


def brier(p: np.ndarray, y: np.ndarray) -> float:
    onehot = np.zeros_like(p)
    onehot[np.arange(len(y)), y] = 1.0
    return float(np.mean(np.sum((p - onehot) ** 2, axis=1)))
