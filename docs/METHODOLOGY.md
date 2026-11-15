# How the ratings work

> **Model v1.0** · English translation of [METODOLOJI.md](METODOLOJI.md), the Turkish original. This document is the source of the site's English methodology page.

This page explains how the ratings of every club in Turkey's professional leagues (Süper Lig, 1. Lig, 2. Lig, 3. Lig) are calculated. There are formulas, but each comes with a plain explanation and a real match as an example. All the code and data are open: you can produce the same ratings yourself (see [Calculate it yourself](#10-calculate-it-yourself)).

## 1. What is Elo?

Elo is a rating system first built to rank chess players. The idea is simple: every club has a rating. When two clubs meet, the difference between their ratings says how much of a favourite each is. After the match the clubs pass points to each other: what the loser loses, the winner wins.

The key point: **an expected result moves few points, a surprise moves many.** When the favourite wins it gains a few points, because that was expected. When the weaker club beats the favourite it gains a lot. Over time every club's rating settles where its real strength is.

The **differences** between ratings matter more than the ratings themselves. A club 200 points ahead carries an "expected score" of about 76% against its opponent.

## 2. Formula

```
Home side's expected score:   E = 1 / (1 + 10^( −(R_home + H − R_away) / 400 ))
Rating change after the match: Δ = K × W × G × (S − E)
                               R_home ← R_home + Δ      R_away ← R_away − Δ
```

| Symbol | Meaning | Value (v1.0) |
|---|---|---|
| R | The club's rating before the match | — |
| H | Home advantage, in points | 65 (0 on neutral ground) |
| E | Expected score: win probability plus half the draw probability (0 to 1) | — |
| S | Actual result: win 1, draw 0.5, loss 0 | — |
| K | How far one match can move the ratings at most | 24 |
| W | Competition weight | See §4 |
| G | Goal-margin multiplier | See §4 |

## 3. A real match: Galatasaray 2-1 Fenerbahçe (26 October 2026)

1. **Ratings before the match:** Galatasaray 1617.7, Fenerbahçe 1622.6. Galatasaray played at home, so it gets 65 points of home advantage.
2. **Difference:** 1617.7 + 65 − 1622.6 = **60.1 points** in Galatasaray's favour.
3. **Expected score:** E = 1 / (1 + 10^(−60.1 / 400)) = **0.586**. Galatasaray were slight favourites.
4. **Result:** Galatasaray won, S = 1. A one-goal win: G = 1. A league match: W = 1.
5. **Change:** Δ = 24 × 1 × 1 × (1 − 0.586) = **+9.9**. Galatasaray rose to 1627.7, Fenerbahçe fell to 1612.7.

Had the match been drawn, Galatasaray would have lost 24 × (0.5 − 0.586) = −2.1 points. As favourites, a draw is a small loss for them.

## 4. Home advantage, goal margin and competition weights

**Home advantage (H):** home clubs in Turkey do clearly better, so the home side gets a 65-point advantage. The Super Cup, cup finals and play-off finals are played on neutral ground, so there H = 0. Home advantage shrank in the pandemic's empty stadiums: in the data the home side's mean score is 0.582 with crowds and 0.566 without, so in that period H = 50.

**Goal margin (G):** a big win says more. For a one-goal margin G = 1, for two goals 1.5, for three or more (11 + margin) / 8: 1.75 for three goals, 2 for five. The test showed that counting the goal margin clearly improves the predictions.

**Extra time and penalties:** a match that goes to extra time counts with its 120-minute result. A match decided on penalties counts as a draw: whoever goes through, a shoot-out says very little about a club's strength.

**Competition weight (W):**

| Match | W |
|---|---|
| League and play-off | 1 |
| Turkish Cup (Ziraat Türkiye Kupası) | 0.75 (final 1). Big clubs rotate in the early rounds |
| Super Cup | 0.75 |
| UEFA competitions | 1 |
| Cup match against an amateur club | 1.5 times the cup weight. The test showed these matches are informative |

**Forfeits** are left out of the ratings, because they were not played. About 205 of the 212 forfeits are the remaining matches of clubs that withdrew from their league. Counting them would hand free points to whoever met that club after an earthquake or a withdrawal. The official result still stands: it is used in the league tables, for promotion and relegation, and for cup bonuses.

## 5. What happens between seasons?

Every summer, before the new season, these steps are applied in order:

1. **Promotion and relegation adjustment:** a promoted club gains points, a relegated club loses them: 30 points across the Süper Lig / 1. Lig line, 25 across 1. Lig / 2. Lig, 20 across 2. Lig / 3. Lig.
2. **Cup bonus** (during the season, right after the final): +15 for the Turkish Cup winners, +5 for the Super Cup winners. The bonus shows as its own line in the club's rating history.
3. **Pull to the mean:** every club's rating moves 30% of the way to its league's mean. Squads change over the summer: last season's best and worst clubs start the new one a little closer to the middle. This step does not change the league's total. A club far from the mean loses a lot: Galatasaray, 290 points above the mean, started 2025-26 with 87 points fewer. Pulling to each club's own mean over its last three seasons instead was tested; big clubs lose less, but the predictions get worse ([backtest.md](backtest.md), in Turkish).
4. **Newcomers:** a club promoted from amateur football to the 3. Lig starts 50 points above the 3. Lig mean. The data shows these clubs play at or slightly above the 3. Lig average in their first season. A club that dropped to amateur football and came back starts like a newcomer. In these clubs' first 10 matches K is 1.5 times larger, so their ratings settle quickly.
5. **Fixing the scale:** the same number is added to or taken from every rating so that the 3. Lig mean is 1000. This changes no ranking and no prediction; it only stops the ratings drifting over time.

## 6. European matches and amateur clubs

**European competitions:** only the Turkish club's rating changes. The foreign opponent's rating comes from its **UEFA club coefficient** that season:

```
Opponent's rating = 1061 + 140 × ln(1 + UEFA club coefficient)
```

| UEFA coefficient | 1 | 5 | 20 | 50 | 100 | 140 |
|---|---|---|---|---|---|---|
| Opponent's rating | 1158 | 1312 | 1488 | 1612 | 1708 | 1755 |

The two numbers in this formula are estimated from the results of the 446 European matches Turkish clubs have played since 2016-17, and estimated again in every run. So European matches give Turkish clubs no free points overall: a club that does better than expected gains, one that does worse loses. Home advantage in Europe is measured from these matches too: 73 points.

*Example:* Lille 2-4 Galatasaray (21 October 2026, Champions League). Lille's coefficient is 68.75, so its rating is ~1656. Lille were at home, so Galatasaray's (1593) expected score was 0.31. Galatasaray won by two goals (G = 1.5). Change: 24 × 1 × 1.5 × (1 − 0.31) = **+24.7**.

There is no separate multiplier for the Champions League, Europa League and Conference League. The level of the competition is already in the opponent's coefficient: beating Bayern is worth far more than beating a low-coefficient side. The test showed a separate competition term adds nothing.

**Amateur clubs (Turkish Cup):** amateur clubs met in the cup have a fixed rating equal to the 3. Lig mean (1000). Only the professional club's rating changes.

## 7. Starting ratings and the warm-up

The calculation starts in the **2016-17 season**. That season every club starts at a fixed rating for its league's level: Süper Lig 1360, 1. Lig 1220, 2. Lig 1100, 3. Lig 1000. Then every match is processed in date order up to today.

The first five seasons (2016-17 to 2020-21) are a **warm-up**: ratings need time to move away from their starting values. The site's tables and charts start in **2021-22**. The seasons disrupted by the pandemic are not shown either, but they still help the ratings settle.

## 8. How were the parameters chosen?

The "right" parameter is the one that best predicts results. Every match was predicted (home win / draw / away win) using only the ratings from before it, and the predictions were scored with **log-loss**: an error measure that punishes confident wrong predictions hard. Lower is better.

The parameters were tuned on the 2021-22 to 2023-24 seasons, then checked on the unseen seasons from 2024-25 to today:

| Model | Log-loss on the check seasons |
|---|---|
| The same prediction for every match (home 45%, draw 26%, away 28%) | 1.074 |
| Only which league each club plays in | 1.069 |
| Elo with the planned starting values | 0.990 |
| **Elo v1.0** | **0.980** |

A value was changed from its planned starting value only when it did clearly better on both the tuning and the check seasons; the others were left as they were. Detailed tables: [backtest.md](backtest.md) (in Turkish).

Options tested and **not** adopted:
- **A Süper Lig title bonus:** adds nothing to the predictions. The champions already earned their rating by winning their matches.
- **Leaving out European matches:** makes domestic predictions neither better nor worse. European matches are real matches, so they count with full weight.

## 9. Limits

Elo only looks at results. It does not know about:
- injuries, suspensions, transfers or managerial changes;
- rotation (for example fielding reserves before a European match);
- how a first-leg score shapes the second leg (a club 4-0 up plays the return at ease).

All of these show up in results, so the ratings correct themselves over time. But a single result sometimes reflects such effects more than a club's real strength.

European opponents' strength comes from the five-year UEFA coefficient, which changes slowly. A club on the rise may be stronger than it looks.

## 10. Calculate it yourself

```bash
git clone <repository address>
cd turkish-leagues-elo/pipeline
uv sync
uv run tlelo elo          # writes the ratings to data/ratings/
uv run tlelo backtest     # rebuilds the test report docs/backtest.md
```

The match data is ready in the repository (`data/`). To download the raw pages again, see [data/README.md](../data/README.md) (in Turkish).

## 11. Version history

| Version | Date | Change |
|---|---|---|
| v1.0 | 14 November 2026 | First version |

## 12. Data sources

- **Domestic matches:** [Turkish Football Federation](https://www.tff.org). Used non-commercially, with the source named.
- **European matches and UEFA coefficients:** the UEFA competition pages of the English [Wikipedia](https://en.wikipedia.org) ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)). Cross-checked against [openfootball](https://github.com/openfootball/champions-league) (CC0).
