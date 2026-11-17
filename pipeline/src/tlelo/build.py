"""Write normalized CSVs (matches, teams) from the cached pages."""

from __future__ import annotations

import csv
import logging
from collections import Counter, defaultdict
from dataclasses import asdict, fields
from pathlib import Path

from tlelo.europe.collect import EuropeMatch, SeasonData
from tlelo.tff.collect import CompetitionData, Match

log = logging.getLogger(__name__)

MATCH_COLUMNS = [f.name for f in fields(Match)]
EUROPE_COLUMNS = [f.name for f in fields(EuropeMatch)]
COMPETITION_ORDER = {"SL": 0, "1L": 1, "2L": 2, "3L": 3, "TK": 4, "SK": 5}


def _write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if v is None else v for k, v in row.items()})


def _write_seasons(path: Path, columns: list[str], rows: list[dict], seasons: set[str]) -> None:
    """Write ``rows`` for ``seasons`` and keep the file's rows of every other season."""
    if path.exists():
        with path.open(encoding="utf-8", newline="") as fh:
            kept = [r for r in csv.DictReader(fh) if r["season"] not in seasons]
        rows = sorted(kept + rows, key=lambda r: r["season"])  # stable: order within a season stays
    _write_csv(path, columns, rows)


def write_matches(data_dir: Path, competitions: list[CompetitionData]) -> dict[str, int]:
    """One CSV per season: ``data/matches/<season>.csv``."""
    by_season: dict[str, list[Match]] = defaultdict(list)
    for comp in competitions:
        by_season[comp.comp.season].extend(comp.matches)
    counts = {}
    for season, matches in sorted(by_season.items()):
        matches.sort(
            key=lambda m: (
                m.date.isoformat() if m.date else "9999",
                m.time or "",
                COMPETITION_ORDER[m.competition],
                m.match_id,
            )
        )
        _write_csv(
            data_dir / "matches" / f"{season}.csv", MATCH_COLUMNS, [asdict(m) for m in matches]
        )
        counts[season] = len(matches)
    return counts


def write_europe(europe_dir: Path, seasons: list[SeasonData]) -> tuple[int, int]:
    """``europe/matches.csv`` (Turkish clubs' matches) and ``europe/coefficients.csv``.

    The coefficient table keeps every club found in that season's draw tables. Seasons not
    in ``seasons`` keep their rows (``europe-build --current-only``).
    """
    built = {s.season for s in seasons}
    matches = [m for s in seasons for m in s.matches]
    _write_seasons(
        europe_dir / "matches.csv",
        EUROPE_COLUMNS,
        [{**asdict(m), "tr_home": int(m.tr_home)} for m in matches],
        built,
    )
    coef_rows = [
        {"season": s.season, "team": title, "name": name, "association": assoc, "coefficient": v}
        for s in seasons
        for title, (name, assoc, v) in sorted(s.coefficients.items())
    ]
    _write_seasons(
        europe_dir / "coefficients.csv",
        ["season", "team", "name", "association", "coefficient"],
        coef_rows,
        built,
    )
    assoc_rows = [
        {"season": s.season, "association": title, "country": name, "coefficient": v}
        for s in seasons
        for title, (name, v) in sorted(s.associations.items(), key=lambda kv: -kv[1][1])
    ]
    _write_seasons(
        europe_dir / "association_coefficients.csv",
        ["season", "association", "country", "coefficient"],
        assoc_rows,
        built,
    )
    return len(matches), len(coef_rows)


def write_teams(data_dir: Path) -> int:
    """``teams.csv`` (one row per club), ``team_names.csv`` and ``team_seasons.csv``.

    Read from every ``matches/<season>.csv``, so a ``build --current-only`` keeps the other
    seasons. A club's league in a season comes from its league matches; clubs that only
    appear in the cup that season were amateur (PGL / BAL) at the time.
    """
    names: dict[tuple[int, str], Counter[str]] = defaultdict(Counter)
    leagues: dict[tuple[int, str], tuple[str, str]] = {}
    for path in sorted((data_dir / "matches").glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as fh:
            for m in csv.DictReader(fh):
                for side in ("home", "away"):
                    key = (int(m[f"{side}_id"]), m["season"])
                    names[key][m[f"{side}_name"]] += 1
                    if m["stage"] == "league":
                        leagues[key] = (m["competition"], m["group"])

    name_rows = [
        {"team_id": tid, "season": season, "name": counter.most_common(1)[0][0]}
        for (tid, season), counter in sorted(names.items())
    ]
    season_rows = [
        {"team_id": tid, "season": season, "competition": comp, "group": group}
        for (tid, season), (comp, group) in sorted(leagues.items())
    ]

    teams: dict[int, dict] = {}
    for row in name_rows:  # sorted by season, so the last name wins
        t = teams.setdefault(
            row["team_id"], {"team_id": row["team_id"], "first_seen": row["season"]}
        )
        t["name"], t["last_seen"] = row["name"], row["season"]
    pro_seasons = Counter(tid for tid, _ in leagues)
    for tid, t in teams.items():
        t["pro_seasons"] = pro_seasons.get(tid, 0)

    _write_csv(
        data_dir / "teams.csv",
        ["team_id", "name", "first_seen", "last_seen", "pro_seasons"],
        [teams[t] for t in sorted(teams)],
    )
    _write_csv(data_dir / "team_names.csv", ["team_id", "season", "name"], name_rows)
    _write_csv(
        data_dir / "team_seasons.csv", ["team_id", "season", "competition", "group"], season_rows
    )
    return len(teams)
