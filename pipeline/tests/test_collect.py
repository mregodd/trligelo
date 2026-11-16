"""Record-level rules: forfeit detection, detail selection, standings check."""

from datetime import date

import pytest

from tlelo.http import MissingPage
from tlelo.tff.collect import (
    CompetitionData,
    Match,
    _apply_detail,
    apply_overrides,
    load_overrides,
    needs_detail,
)
from tlelo.tff.crawl import CompetitionPage, GroupTable, weeks_to_read
from tlelo.tff.parse import FixtureRow, StandingRow
from tlelo.validate import check_competition, computed_table

SL = CompetitionPage("SL", "2022-23", 1628, current=False)
TK = CompetitionPage("TK", "2016-17", 1425, current=False)


def match(mid, home, away, hg, ag, **kw):
    defaults = dict(
        season="2022-23",
        competition="SL",
        stage="league",
        round=None,
        group=None,
        week=1,
        date=date(2023, 4, 19),
        time="20:00",
        home_name=f"T{home}",
        away_name=f"T{away}",
    )
    defaults.update(kw)
    return Match(match_id=mid, home_id=home, away_id=away, home_goals=hg, away_goals=ag, **defaults)


class FakeClient:
    def __init__(self, pages):
        self.pages = pages

    def is_cached(self, params):
        return params.get("macId") in self.pages

    def get(self, params, refresh=False):
        try:
            return self.pages[params["macId"]]
        except KeyError:
            raise MissingPage(str(params)) from None


NO_OFFICIALS = '<a id="lnkStad" href="x?stadId=6097">VODAFONE PARK</a><div class="dtMacBilgisiHakemler"> </div>'
WITH_OFFICIALS = '<div class="dtMacBilgisiHakemler"><a>X(Hakem)</a></div>'


def test_three_nil_without_referees_is_a_forfeit():
    data = CompetitionData(SL, [])
    m = match(1, 10, 20, 3, 0)
    _apply_detail(FakeClient({1: NO_OFFICIALS}), m, data)
    assert m.status == "forfeit" and m.venue_id == 6097


def test_real_three_nil_stays_played():
    data = CompetitionData(SL, [])
    m = match(2, 10, 20, 0, 3)
    _apply_detail(FakeClient({2: WITH_OFFICIALS}), m, data)
    assert m.status == "played"


def test_unverified_three_nil_is_reported():
    data = CompetitionData(SL, [])
    m = match(3, 10, 20, 3, 0)
    _apply_detail(FakeClient({}), m, data)
    assert m.status == "played" and data.issues


def test_needs_detail_selection():
    assert needs_detail(SL, match(1, 1, 2, 3, 0))
    assert not needs_detail(SL, match(2, 1, 2, 2, 1))
    assert needs_detail(SL, match(3, 1, 2, 1, 1, stage="playoff", round="Final"))
    assert needs_detail(TK, match(4, 1, 2, 1, 0, stage="cup", round="Final"))
    assert not needs_detail(TK, match(5, 1, 2, 1, 0, stage="cup", round="Yarı Final"))


def test_computed_table_and_check():
    data = CompetitionData(
        SL,
        [
            match(1, 10, 20, 2, 1),
            match(2, 20, 10, 1, 1),
            match(3, 10, 20, None, None, status="not_played"),
            match(4, 10, 20, 1, 0, stage="playoff"),  # play-offs are not in the table
        ],
    )
    table = computed_table(data, None)
    assert table[10] == [2, 1, 1, 0, 3, 2, 4]
    assert table[20] == [2, 0, 1, 1, 2, 3, 1]

    data.standings[None] = [
        StandingRow(10, 2, 1, 1, 0, 3, 2, 4),
        StandingRow(20, 2, 0, 1, 1, 2, 3, -2),  # points deduction: not a mismatch
    ]
    (check,) = check_competition(data)
    assert check.mismatches == []
    assert len(check.point_differences) == 1


OVERRIDES = """match_id,status,home_goals,away_goals,note,source
1,forfeit,3,0,"awarded, no score in fixture",x
2,double_forfeit,,,both lost,x
"""


def test_overrides_fill_awarded_results(tmp_path):
    path = tmp_path / "match_overrides.csv"
    path.write_text(OVERRIDES, encoding="utf-8")
    data = CompetitionData(
        SL,
        [
            match(1, 10, 20, None, None, status="not_played"),
            match(2, 10, 30, None, None, status="not_played"),
            match(3, 20, 30, 1, 1),
        ],
    )
    apply_overrides(data, load_overrides(path))
    assert (data.matches[0].status, data.matches[0].regular_score) == ("forfeit", (3, 0))
    assert data.matches[1].status == "double_forfeit"

    table = computed_table(data, None)
    assert table[10] == [2, 1, 0, 1, 3, 3, 3]  # won 3-0, lost the double forfeit 0-3
    assert table[30] == [2, 0, 1, 1, 1, 4, 1]


def test_overrides_reject_unknown_status(tmp_path):
    path = tmp_path / "match_overrides.csv"
    path.write_text("match_id,status,home_goals,away_goals,note,source\n1,hukmen,3,0,,\n")
    with pytest.raises(ValueError):
        load_overrides(path)
    assert load_overrides(tmp_path / "missing.csv") == {}


def test_the_coming_week_is_read_too_for_its_kick_off_dates():
    def table(*weeks):  # (week, played) pairs
        rows = [FixtureRow(i, w, None, 1, "A", 2, "B", (1, 0) if p else None)
                for i, (w, p) in enumerate(weeks)]  # fmt: skip
        return GroupTable(None, None, "", rows)

    live = CompetitionPage("SL", "2026-27", 1, current=True)
    assert weeks_to_read(live, table((1, True), (2, True), (3, False), (4, False))) == [1, 2, 3]
    assert weeks_to_read(live, table((1, False), (2, False))) == [1]  # before the first round
    assert weeks_to_read(live, table((1, True), (2, True))) == [1, 2]  # all played
    # A finished season's unplayed weeks never come (2019-20 stopped in the pandemic).
    assert weeks_to_read(SL, table((1, True), (2, True), (3, False))) == [1, 2]
