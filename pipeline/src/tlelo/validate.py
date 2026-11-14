"""Check parsed matches against the standings tables TFF publishes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from tlelo.tff.collect import CompetitionData

# Columns compared: played, won, drawn, lost, goals for, goals against.
STAT_NAMES = ("O", "G", "B", "M", "A", "Y")


@dataclass(slots=True)
class GroupCheck:
    label: str
    teams: int
    mismatches: list[str] = field(default_factory=list)
    point_differences: list[str] = field(default_factory=list)  # usually points deductions


def computed_table(data: CompetitionData, group: str | None) -> dict[int, list[int]]:
    """team_id -> [O, G, B, M, A, Y, P] from league matches with a result."""
    table: dict[int, list[int]] = defaultdict(lambda: [0] * 7)
    for m in data.matches:
        if m.stage != "league" or m.group != group:
            continue
        if m.status == "double_forfeit":  # both sides counted as 0-3 losers
            sides = ((m.home_id, 0, 3), (m.away_id, 0, 3))
        elif m.home_goals is None or m.away_goals is None:
            continue
        else:
            sides = (
                (m.home_id, m.home_goals, m.away_goals),
                (m.away_id, m.away_goals, m.home_goals),
            )
        for team, gf, ga in sides:
            row = table[team]
            row[0] += 1
            row[4] += gf
            row[5] += ga
            if gf > ga:
                row[1] += 1
                row[6] += 3
            elif gf == ga:
                row[2] += 1
                row[6] += 1
            else:
                row[3] += 1
    return table


def check_competition(data: CompetitionData) -> list[GroupCheck]:
    checks = []
    for group, standings in data.standings.items():
        label = f"{data.comp.label()}" + (f" / {group}" if group else "")
        check = GroupCheck(label, len(standings))
        ours = computed_table(data, group)
        if not standings:
            check.mismatches.append("no standings table on page")
        for row in standings:
            theirs = [row.played, row.won, row.drawn, row.lost, row.goals_for, row.goals_against]
            mine = ours.get(row.team_id, [0] * 7)
            diffs = [
                f"{name} {a}≠{b}"
                for name, a, b in zip(STAT_NAMES, mine[:6], theirs, strict=True)
                if a != b
            ]
            if diffs:
                check.mismatches.append(f"team {row.team_id}: " + ", ".join(diffs))
            elif mine[6] != row.points:
                check.point_differences.append(f"team {row.team_id}: {mine[6]} vs TFF {row.points}")
        missing = set(ours) - {r.team_id for r in standings}
        if standings and missing:
            check.mismatches.append(f"teams not in TFF table: {sorted(missing)}")
        checks.append(check)
    return checks
