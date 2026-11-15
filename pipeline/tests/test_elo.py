"""Elo engine rules on tiny hand-made seasons, and the two statistical fits."""

from datetime import date

import numpy as np
import pytest

from tlelo.elo.data import Dataset, Game, Side, league_champion
from tlelo.elo.engine import Engine, EuropeModel, expected, margin_factor
from tlelo.elo.fit import KAPPA, OrderedLogit, fit_europe
from tlelo.elo.params import Params

EU = EuropeModel(a=1000.0, b=150.0, home=70.0)
FLAT = Params(regression=0.0, promotion=(0.0, 0.0, 0.0), bonus_cup=0.0, bonus_supercup=0.0)


def pro(team):
    return Side("pro", team, f"T{team}")


def game(home, away, goals, *, season="2016-17", day=1, comp="SL", stage="league", rnd=None,
         neutral=False, pens=None, tr_venue=False, closed=False):  # fmt: skip
    h, a = goals
    return Game(
        key=f"{comp}:{day}:{home.name}", season=season, date=date(2016, 8, day), time="",
        competition=comp, stage=stage, round=rnd, home=home, away=away, goals=goals,
        pens=pens, result90="H" if h > a else "A" if h < a else "D", neutral=neutral,
        home_is_tr_venue=tr_venue, closed=closed,
    )  # fmt: skip


def run(games, tiers, params=FLAT, champions=None):
    seasons = sorted(tiers)
    by_season = {s: [g for g in games if g.season == s] for s in seasons}
    data = Dataset(seasons, by_season, tiers, champions=champions or {})
    return Engine(data, params, EU).run()


def test_expected_and_margin():
    assert expected(0) == 0.5
    assert expected(200) == pytest.approx(0.7597, abs=1e-4)
    assert [margin_factor(n) for n in (0, 1, -2, 3, 5)] == [1.0, 1.0, 1.5, 1.75, 2.0]


def test_one_game_is_zero_sum():
    # Seeds: SL 1450, 3L 1000 for the anchor; both clubs SL, the home side wins 2-0.
    tiers = {"2016-17": {1: 1, 2: 1, 9: 4}}
    res = run([game(pro(1), pro(2), (2, 0))], tiers)
    (rec,) = res.records
    e = expected(65)  # equal ratings plus home advantage
    assert rec.expected == pytest.approx(e)
    assert rec.delta_home == pytest.approx(20 * 1.5 * (1 - e))  # K * G(2 goals) * (S - E)
    assert rec.delta_away == pytest.approx(-rec.delta_home)
    assert res.ratings[1] + res.ratings[2] == pytest.approx(2900)


def test_neutral_ground_and_shootout_is_a_draw():
    tiers = {"2016-17": {1: 1, 2: 1, 9: 4}}
    final = game(pro(1), pro(2), (1, 1), comp="TK", stage="cup", rnd="Final", neutral=True,
                 pens=(4, 3))  # fmt: skip
    res = run([final], tiers, FLAT.with_(bonus_cup=15.0))
    (rec,) = res.records
    assert rec.h == 0 and rec.delta_home == 0  # equal ratings, draw, no home advantage
    assert res.ratings[1] == pytest.approx(1465)  # cup bonus for the shoot-out winner
    assert [a.kind for a in res.adjustments if a.team == 1] == ["seed", "cup"]


def test_amateur_and_foreign_sides_do_not_move():
    tiers = {"2016-17": {1: 1, 9: 4}}
    amateur = Side("amateur", 500, "A")
    foreign = Side("foreign", None, "F", coefficient=20.0)
    cup = game(amateur, pro(1), (1, 0), comp="TK", stage="cup", day=2)
    eu = game(foreign, pro(1), (0, 0), comp="UEL", stage="europe", day=3)
    res = run([cup, eu], tiers)
    cup_rec, eu_rec = res.records
    assert cup_rec.r_home == FLAT.anchor + FLAT.amateur and cup_rec.delta_home == 0
    assert cup_rec.weight == FLAT.w_cup * FLAT.w_amateur
    assert eu_rec.r_home == pytest.approx(EU.rating(20.0, "UEL")) and eu_rec.h == EU.home


def test_european_match_played_in_turkey():
    tiers = {"2016-17": {1: 1, 9: 4}}
    foreign = Side("foreign", None, "F", coefficient=5.0)
    # BATE - Konyaspor 2022 was played in Konya: the Turkish "away" side is at home.
    res = run([game(foreign, pro(1), (0, 1), comp="UECL", stage="europe", tr_venue=True)], tiers)
    assert res.records[0].h == -EU.home


def test_season_transition():
    tiers = {
        "2016-17": {1: 1, 2: 2, 3: 4, 4: 4},
        "2017-18": {1: 2, 2: 1, 3: 4, 4: 4, 5: 4},  # 1 and 2 swap leagues, 5 is new
    }
    p = FLAT.with_(promotion=(30.0, 25.0, 20.0), regression=0.5, newcomer=50.0)
    games = [game(pro(3), pro(4), (3, 0), day=5)]  # spreads the 3. Lig ratings
    res = run(games, tiers, p)
    kinds = {(a.team, a.kind) for a in res.adjustments if a.season == "2017-18"}
    assert (1, "relegation") in kinds and (2, "promotion") in kinds
    assert (5, "newcomer") in kinds
    r = res.ratings
    bottom = [r[3], r[4], r[5]]
    assert sum(bottom) / 3 == pytest.approx(p.anchor)  # anchor
    # Regression halves the gap between the two continuing 3. Lig clubs; the newcomer
    # sits 50 above their mean (before the common anchor shift).
    gap_before = res.records[0].delta_home * 2
    assert r[3] - r[4] == pytest.approx(gap_before * 0.5)
    assert r[5] - (r[3] + r[4]) / 2 == pytest.approx(50.0)
    # 1 was relegated (-30) and 2 promoted (+30): the gap between them grew by 60.
    assert r[2] - r[1] == pytest.approx(1275 - 1450 + 60)


def test_title_bonus_variant():
    tiers = {"2016-17": {1: 1, 2: 1, 9: 4}, "2017-18": {1: 1, 2: 1, 9: 4}}
    res = run([], tiers, FLAT.with_(bonus_champion=30.0), champions={"2016-17": 2})
    assert res.ratings[2] - res.ratings[1] == pytest.approx(30.0)


def test_league_champion_counts_forfeits_and_needs_a_finished_season():
    rows = [
        dict(home_id="1", away_id="2", home_goals="0", away_goals="1", status="played"),
        dict(home_id="3", away_id="1", home_goals="0", away_goals="3", status="forfeit"),
        dict(home_id="2", away_id="3", home_goals="", away_goals="", status="double_forfeit"),
    ]
    assert league_champion(rows) == 1  # 3 pts like 2, better goal difference (+2 vs -2)
    assert league_champion([*rows, dict(status="not_played")]) is None


def test_ordered_logit_recovers_its_parameters():
    rng = np.random.default_rng(1)
    truth = OrderedLogit(beta=0.6, c1=-0.6, c2=0.6)
    diff = rng.normal(60, 150, 20000)
    u = rng.random(len(diff))
    cum = np.cumsum(truth.probabilities(diff), axis=1)
    y = (u[:, None] > cum).sum(axis=1)
    fit = OrderedLogit.fit(diff, y)
    assert fit.beta == pytest.approx(0.6, abs=0.05)
    assert (fit.c1, fit.c2) == pytest.approx((-0.6, 0.6), abs=0.06)


def test_europe_fit_recovers_a_and_b():
    from tlelo.elo.engine import GameRecord

    rng = np.random.default_rng(2)
    a, b, home = 1050.0, 140.0, 70.0
    records = []
    for i in range(3000):
        coef = float(rng.uniform(1, 120))
        tr = Side("pro", 1, "T")
        foreign = Side("foreign", None, "F", coefficient=coef)
        r_tr = float(rng.normal(1500, 80))
        opp = a + b * np.log1p(coef)
        tr_home = i % 2 == 0
        h = home if tr_home else -home
        p_win = 1 / (1 + np.exp(-KAPPA * (r_tr + h - opp)))
        s = 1.0 if rng.random() < p_win else 0.0
        goals = (1, 0) if (s == 1.0) == tr_home else (0, 1)
        g = game(tr if tr_home else foreign, foreign if tr_home else tr, goals, comp="UEL",
                 stage="europe")  # fmt: skip
        rh, ra = (r_tr, opp) if tr_home else (opp, r_tr)
        records.append(GameRecord(g, rh, ra, home, 0.5, 1.0, 0.0, 0.0))
    model, _, n = fit_europe(records, Params(), EuropeModel(1150.0, 150.0, 65.0))
    assert n == 3000
    assert model.b == pytest.approx(b, rel=0.12)
    assert model.home == pytest.approx(home, abs=20)
    assert model.rating(20.0, "UEL") == pytest.approx(a + b * np.log1p(20.0), abs=25)


def test_regression_toward_own_mean():
    # With the club's own mean over one season as the target, nobody is pulled at all.
    tiers = {"2016-17": {1: 4, 2: 4}, "2017-18": {1: 4, 2: 4}}
    games = [game(pro(1), pro(2), (3, 0))]
    p = FLAT.with_(regression=0.5, regression_own=1.0, regression_seasons=1)
    res = run(games, tiers, p)
    assert [a.delta for a in res.adjustments if a.kind == "regression"] == [0.0, 0.0]
    league = run(games, tiers, p.with_(regression_own=0.0))
    assert all(a.delta != 0 for a in league.adjustments if a.kind == "regression")
