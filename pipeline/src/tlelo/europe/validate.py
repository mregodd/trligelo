"""Consistency checks for the European matches (no second source needed).

* a group stage gives every club 6 matches, a league phase 8 (6 in the Conference League);
* knock-out ties have two legs, except where UEFA played single matches (2020-21
  qualifying during the pandemic, the August 2020 final tournaments);
* matches of finished seasons all have a result, a date and both clubs identified.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from tlelo.europe.collect import TWO_LEGGED, EuropeMatch, SeasonData

# (season, competition) -> rounds UEFA played as single matches.
SINGLE_LEG = {
    ("2019-20", "UCL"): {"QF", "SF"},
    ("2019-20", "UEL"): {"QF", "SF"},
    ("2020-21", "UCL"): {"PR", "Q1", "Q2", "Q3"},
    ("2020-21", "UEL"): {"PR", "Q1", "Q2", "Q3", "PO"},
}


def _phase_size(m: EuropeMatch) -> int | None:
    if m.round == "GS":
        return 6
    if m.round == "LP":
        return 6 if m.competition == "UECL" else 8
    return None


def check_season(data: SeasonData, *, finished: bool = True) -> list[str]:
    out = []
    phase: Counter[tuple] = Counter()
    ties: dict[tuple, list[EuropeMatch]] = defaultdict(list)
    for m in data.matches:
        if (size := _phase_size(m)) is not None:
            phase[(m.competition, m.round, m.team_id or m.home_name, size)] += 1
        if m.round in TWO_LEGGED:
            ties[(m.competition, m.round, m.team_id, m.opponent)].append(m)
        if finished and m.status == "not_played":
            out.append(f"no result: {m.date} {m.home_name}-{m.away_name} ({m.source})")
        opp_assoc = m.away_assoc if m.tr_home else m.home_assoc
        if opp_assoc not in data.associations:
            out.append(f"no association coefficient: {opp_assoc} ({m.opponent})")

    for (comp, rnd, team, size), n in sorted(phase.items(), key=str):
        if n != size:
            out.append(f"{comp} {rnd}: club {team} has {n} matches, expected {size}")
    for (comp, rnd, team, opp), legs in sorted(ties.items(), key=str):
        single = rnd in SINGLE_LEG.get((data.season, comp), set())
        if len(legs) != (1 if single else 2):
            out.append(f"{comp} {rnd}: club {team} vs {opp}: {len(legs)} match(es)")
    return out
