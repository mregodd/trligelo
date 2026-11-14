"""``tlelo backtest``: the numbers behind docs/faz-2-rapor.md, as a Markdown report.

Everything here is recomputed from the data on every run (about a minute).
"""

from __future__ import annotations

import math
import statistics as st
from dataclasses import dataclass

import numpy as np
from scipy.stats import chi2

from tlelo.elo import backtest as bt
from tlelo.elo.data import Dataset
from tlelo.elo.engine import RunResult
from tlelo.elo.fit import OrderedLogit, fit_europe, run_model
from tlelo.elo.params import MODEL_VERSION, V1, Params

LEAGUE_NAMES = {1: "Süper Lig", 2: "1. Lig", 3: "2. Lig", 4: "3. Lig"}


@dataclass(slots=True)
class Evaluated:
    res: RunResult
    tune: np.ndarray  # per-game log-loss
    holdout: np.ndarray


def evaluate(data: Dataset, params: Params) -> Evaluated:
    res = run_model(data, params)
    diff, y, _ = bt.arrays(res, bt.TUNE)
    model = OrderedLogit.fit(diff, y)
    out = []
    for seasons in (bt.TUNE, bt.HOLDOUT):
        d, yy, _ = bt.arrays(res, seasons)
        p = model.probabilities(d)
        out.append(-np.log(np.clip(p[np.arange(len(yy)), yy], 1e-12, 1.0)))
    return Evaluated(res, out[0], out[1])


def paired(a: np.ndarray, b: np.ndarray) -> str:
    d = a - b
    return f"{d.mean():+.4f} ± {d.std(ddof=1) / math.sqrt(len(d)):.4f}"


def _table(head: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


VARIANTS = [
    ("Süper Lig şampiyonluk bonusu +30", dict(bonus_champion=30.0)),
    ("Yükselme/düşme düzeltmesi yok (P = 0)", dict(promotion=(0.0, 0.0, 0.0))),
    ("Kupa bonusu yok (B = 0)", dict(bonus_cup=0.0, bonus_supercup=0.0)),
    ("Avrupa maçları hariç (W = 0)", dict(w_europe=0.0)),
    ("Avrupa maçları yarım ağırlık (W = 0,5)", dict(w_europe=0.5)),
    ("Avrupa'da turnuva terimi (ŞL/AL/KL)", dict(europe_competition_terms=True)),
    ("Gol farkı çarpanı yok (G = 1)", dict(margin=False)),
    ("Geçici K yok", dict(provisional_factor=1.0)),
]


def backtest_report(data: Dataset) -> str:
    plan, v1 = Params(), V1
    ev1 = evaluate(data, v1)
    evp = evaluate(data, plan)
    res = ev1.res
    lines = [
        f"# Geriye dönük test: model {MODEL_VERSION}",
        "",
        "> Bu dosya `uv run tlelo backtest` ile üretilir, elle düzenlenmez. Yorumlar için "
        "bkz. [faz-2-rapor.md](faz-2-rapor.md).",
        "",
        f"- Ayar sezonları: {', '.join(bt.TUNE)}. Kontrol sezonları (ayarda hiç "
        f"kullanılmadı): {', '.join(bt.HOLDOUT)}.",
        "- Ölçüt: iki profesyonel takım arasındaki yurt içi maçlarda 90 dakika sonucunun "
        "(ev sahibi / beraberlik / deplasman) log-loss'u. Düşük olan daha iyi.",
        "",
        "## Tahmin başarısı",
        "",
    ]
    b_t, b_h = bt.base_rates(res)
    t_t, t_h = bt.tier_only(data, res)
    lines += _table(
        ["Model", "Ayar log-loss", "Kontrol log-loss", "Kontrol Brier"],
        [
            ["Sabit oranlar (ev/beraberlik/deplasman sıklığı)", f"{b_t.log_loss:.4f}",
             f"{b_h.log_loss:.4f}", f"{b_h.brier:.4f}"],
            ["Sadece lig seviyesi", f"{t_t.log_loss:.4f}", f"{t_h.log_loss:.4f}",
             f"{t_h.brier:.4f}"],
            ["Elo, plandaki başlangıç değerleri", f"{evp.tune.mean():.4f}",
             f"{evp.holdout.mean():.4f}", f"{bt.holdout_score(evp.res).brier:.4f}"],
            [f"**Elo {MODEL_VERSION}**", f"**{ev1.tune.mean():.4f}**",
             f"**{ev1.holdout.mean():.4f}**", f"**{bt.holdout_score(res).brier:.4f}**"],
        ],
    )  # fmt: skip
    lines += ["", f"Maç sayısı: ayar {len(ev1.tune)}, kontrol {len(ev1.holdout)}.", ""]

    # Per league, holdout.
    diff, y, recs = bt.arrays(res, bt.TUNE)
    model = OrderedLogit.fit(diff, y)
    freq = np.bincount(y, minlength=3) / len(y)
    dh, yh, rh = bt.arrays(res, bt.HOLDOUT)
    p = model.probabilities(dh)
    rows = []
    for comp in ("SL", "1L", "2L", "3L", "TK"):
        idx = np.array([r.game.competition == comp for r in rh])
        if idx.sum() == 0:
            continue
        ll = -np.log(p[idx][np.arange(idx.sum()), yh[idx]]).mean()
        base = -np.log(freq[yh[idx]]).mean()
        rows.append([comp, int(idx.sum()), f"{base:.4f}", f"{ll:.4f}"])
    lines += ["### Kontrol sezonlarında lig bazında", ""]
    lines += _table(["Organizasyon", "Maç", "Sabit oranlar", f"Elo {MODEL_VERSION}"], rows)

    # Each change from the plan, undone one at a time.
    lines += [
        "",
        "## Plandan sapan her değerin etkisi",
        "",
        "Değer plandaki başlangıç değerine geri alınınca log-loss ne kadar değişiyor "
        "(pozitif: geri almak kötüleştiriyor, yani değişiklik işe yarıyor).",
        "",
    ]
    rows = []
    for name in v1.as_dict():
        if getattr(v1, name) == getattr(plan, name):
            continue
        ev = evaluate(data, v1.with_(**{name: getattr(plan, name)}))
        rows.append(
            [
                f"`{name}`",
                getattr(plan, name),
                getattr(v1, name),
                paired(ev.tune, ev1.tune),
                paired(ev.holdout, ev1.holdout),
            ]
        )
    lines += _table(["Parametre", "Plan", MODEL_VERSION, "Ayar farkı", "Kontrol farkı"], rows)

    # Variants asked about.
    lines += [
        "",
        "## Denenen seçenekler",
        "",
        f"{MODEL_VERSION} üzerine tek bir değişiklik (pozitif: seçenek kötüleştiriyor).",
        "",
    ]
    rows = []
    for label, change in VARIANTS:
        ev = evaluate(data, v1.with_(**change))
        rows.append([label, paired(ev.tune, ev1.tune), paired(ev.holdout, ev1.holdout)])
    lines += _table(["Seçenek", "Ayar farkı", "Kontrol farkı"], rows)

    # Europe.
    e = res.europe
    m1, nll1, n = fit_europe(res.records, v1.with_(europe_competition_terms=True), e)
    _, nll0, _ = fit_europe(res.records, v1, e)
    lr = 2 * (nll0 - nll1)
    lines += [
        "",
        "## Avrupa",
        "",
        f"Rakip puanı = {e.a:.0f} + {e.b:.1f} × ln(1 + katsayı). Avrupa'da ev sahibi "
        f"avantajı {e.home:.0f} puan ({n} oynanmış maçtan).",
        "",
    ]
    lines += _table(
        ["UEFA kulüp katsayısı", *[str(c) for c in (1, 5, 10, 20, 50, 100, 140)]],
        [["Rakip puanı", *[f"{e.rating(c, 'UEL'):.0f}" for c in (1, 5, 10, 20, 50, 100, 140)]]],
    )
    offsets = ", ".join(f"{k} {v:+.0f}" for k, v in m1.offsets)
    lines += [
        "",
        f"Turnuva terimi (Şampiyonlar Ligi'ne göre): {offsets}. Olabilirlik oranı "
        f"testi: {lr:.2f}, p = {chi2.sf(lr, 2):.2f}.",
        "",
    ]
    resid = bt.europe_residuals(res, data.seasons)
    lines += _table(
        ["Turnuva", "Maç", "Türk takımının ortalama (S − E) farkı"],
        [[k, n_, f"{v:+.3f}"] for k, (n_, v) in resid.items()],
    )

    # Levels.
    lines += [
        "",
        "## Ligler arası fark",
        "",
        "Kupada farklı liglerden takımların maçları: üst lig takımının ortalama skoru "
        "ve bunun puan karşılığı (`400 × log10(p / (1 − p))`).",
        "",
    ]
    gaps = bt.implied_gap(res, bt.TUNE + bt.HOLDOUT)
    lines += _table(
        ["Eşleşme", "Maç", "Üst ligin ortalama skoru", "Puan farkı karşılığı"],
        [
            [f"{LEAGUE_NAMES[a]} – {LEAGUE_NAMES[b]}", n_, f"{p_:.3f}", f"{g:.0f}"]
            for (a, b), (n_, p_, g) in gaps.items()
        ],
    )
    season = data.seasons[-1]
    tiers = data.tiers[season]
    rows = []
    for tier in (1, 2, 3, 4):
        rs = [res.ratings[t] for t, tr in tiers.items() if tr == tier]
        rows.append(
            [LEAGUE_NAMES[tier], len(rs), f"{min(rs):.0f}", f"{st.mean(rs):.0f}", f"{max(rs):.0f}"]
        )
    allr = [res.ratings[t] for t in tiers]
    lines += ["", f"### Puan dağılımı ({season}, şu an)", ""]
    lines += _table(["Lig", "Takım", "En düşük", "Ortalama", "En yüksek"], rows)
    lines += ["", f"En iyi ile en kötü takım arası: {max(allr) - min(allr):.0f} puan.", ""]
    return "\n".join(lines)
