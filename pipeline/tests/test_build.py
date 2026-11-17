"""A ``--current-only`` build rewrites only the running season and keeps the others."""

import csv

from tlelo.build import write_europe, write_teams
from tlelo.europe.collect import SeasonData

HEADER = "season,competition,stage,group,home_id,home_name,away_id,away_name\n"


def rows(path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_write_teams_reads_every_season_csv(tmp_path):
    matches = tmp_path / "matches"
    matches.mkdir()
    (matches / "2024-25.csv").write_text(
        HEADER + "2024-25,1L,league,,1,ANKARA,2,BURSA\n", encoding="utf-8"
    )
    (matches / "2025-26.csv").write_text(
        HEADER + "2025-26,SL,league,,1,ANKARA FK,3,CORUM\n2025-26,TK,cup,,2,BURSA,4,AMATÖR\n",
        encoding="utf-8",
    )
    assert write_teams(tmp_path) == 4
    teams = {r["team_id"]: r for r in rows(tmp_path / "teams.csv")}
    assert teams["1"] == {
        "team_id": "1",
        "name": "ANKARA FK",
        "first_seen": "2024-25",
        "last_seen": "2025-26",
        "pro_seasons": "2",
    }
    assert teams["4"]["pro_seasons"] == "0"  # cup only: amateur that season
    assert [r["competition"] for r in rows(tmp_path / "team_seasons.csv")] == [
        "1L",
        "SL",
        "1L",
        "SL",
    ]


def test_write_europe_keeps_other_seasons(tmp_path):
    (tmp_path / "coefficients.csv").write_text(
        "season,team,name,association,coefficient\n"
        "2025-26,A_FC,A FC,ENG,10.0\n2026-27,OLD,Old,ESP,1.0\n",
        encoding="utf-8",
    )
    season = SeasonData("2026-27", coefficients={"B_FC": ("B FC", "ITA", 20.5)})
    write_europe(tmp_path, [season])
    assert [(r["season"], r["team"]) for r in rows(tmp_path / "coefficients.csv")] == [
        ("2025-26", "A_FC"),
        ("2026-27", "B_FC"),
    ]
