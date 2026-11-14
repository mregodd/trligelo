"""Wikipedia match boxes, coefficient tables and the Turkish-club records built from them.

The HTML below keeps the structure of Wikipedia's Parsoid output (2018-19 pages) with the
attributes the parser does not use removed.
"""

from datetime import date

from tlelo.europe import parse as p
from tlelo.europe.collect import collect_season, round_code
from tlelo.europe.validate import check_season
from tlelo.europe.wiki import Article, cache_key, page_title, sub_articles, wiki_season

W = "https://en.wikipedia.org/wiki/"


def flag(assoc):
    # Table cells carry Parsoid attributes on the flag span; boxes usually do not.
    return (
        f'<span class="flagicon" data-mw=\'{{"parts":[]}}\'><span class="mw-image-border">'
        f'<a href="{W}{assoc}" title="{assoc}"><img src="x.png"></a></span></span>'
    )


def plain_flag():
    """Association ranking rows: the flag has no link."""
    return '<span class="flagicon"><span class="mw-image-border"><img src="x.png"></span></span>'


def team(title, name, assoc, home=True):
    link = f'<a rel="mw:WikiLink" href="{W}{title}" title="{title}">{name}</a>' if title else name
    return f"{link} {flag(assoc)}" if home else f"{flag(assoc)} {link}"


def box(day, home, score, away, hgoals="", agoals="", extra="", report=2025367):
    return f"""<div class="footballbox">
<div class="fleft"><time><div class="fdate">{day}<span>(<span class="bday dtstart published updated itvstart">{day}</span>)</span></div><div class="ftime">20:00 <span>(21:00 UTC+3)</span></div></time></div>
<table class="fevent"><tbody><tr itemprop="name">
<th class="fhome" itemprop="homeTeam"><span itemprop="name">{home}</span></th><th class="fscore">{score}</th><th class="faway" itemprop="awayTeam"><span itemprop="name">{away}</span></th></tr>
<tr class="fgoals"><td class="fhgoal">{hgoals}</td><td><a rel="mw:ExtLink nofollow" href="https://www.uefa.com/uefaeuropaleague/match/{report}/" class="external text">Report</a></td><td class="fagoal">{agoals}</td></tr>
{extra}</tbody></table><div class="fright"><div itemprop="location"><span itemprop="name address"><a rel="mw:WikiLink" href="{W}Turf_Moor" title="Turf Moor">Turf Moor</a>, <a href="{W}Burnley">Burnley</a></span></div></div></div>
"""


def goal(minute, note=""):
    return f'<li>X <span class="fb-goal"><span title="Goal"><img></span><span> </span><span>{minute}\'{note}</span></span></li>'


ENG = "The_Football_Association"
TFF = "Turkish_Football_Federation"
AET = '1–1 (<a rel="mw:WikiLink" href="https://en.wikipedia.org/wiki/Overtime_(sports)">a.e.t.</a>)'
SHOOTOUT = (
    '<tr><th colspan="3"><a rel="mw:WikiLink" href="x" title="Penalty shoot-out">Penalties</a></th></tr>'
    '<tr class="fgoals"><td class="fhgoal"><ul><li>A</li></ul></td><th>4–3</th><td class="fagoal"></td></tr>'
)


def test_box_after_extra_time_and_penalties():
    html = box(
        "2018-08-16",
        team("Burnley_F.C.", "Burnley", ENG),
        AET,
        team(None, "İstanbul Başakşehir", TFF, home=False),
        hgoals=f"<ul>{goal(102)}</ul>",
        agoals=f"<ul>{goal('90+3', ' (pen.)')}</ul>",
        extra=SHOOTOUT,
    )
    (m,) = p.parse_boxes("<h2>Third qualifying round</h2><h3>Main Path matches</h3>" + html)
    assert m.date == date(2018, 8, 16) and m.time == "20:00"
    assert m.home == p.Side("Burnley F.C.", "Burnley", "The Football Association")
    assert m.away == p.Side(None, "İstanbul Başakşehir", "Turkish Football Federation")
    assert (m.score, m.extra_time, m.regular, m.penalties) == ((1, 1), True, (0, 1), (4, 3))
    assert m.uefa_id == 2025367 and m.venue == "Turf Moor, Burnley"
    assert m.score_text == "1–1 (a.e.t.)"
    assert m.section == "Third qualifying round / Main Path matches"


def test_extra_time_without_goal_minutes_leaves_regular_score_unknown():
    html = box("2018-08-16", team("A", "A", ENG), AET, team("B", "B", TFF, home=False))
    (m,) = p.parse_boxes(html)
    assert m.score == (1, 1) and m.regular is None


def test_unplayed_box():
    (m,) = p.parse_boxes(box("2026-12-10", team("A", "A", ENG), "v", team("B", "B", TFF, False)))
    assert m.score is None and m.score_text == "v"


def cell(title, name, assoc):
    return (
        f"<td>{flag(assoc)} "
        + f'<a rel="mw:WikiLink" href="{W}{title}" title="{title}">{name}</a><sup>[Q3]</sup></td>'
    )


COEFFS = f"""<table class="wikitable"><tbody>
<tr><th>Team</th><th><span title="UEFA Club Coefficient">Coeff.</span></th><th>Team</th><th>Coeff.</th></tr>
<tr>{cell("Burnley_F.C.", "Burnley", ENG)}<td>15.921</td>{cell("S.L._Benfica", "Benfica", "Portuguese_Football_Federation")}<td>80.000</td></tr>
<tr><td>Pot 1</td></tr>
</tbody></table>
<table><tr><th>Team</th><th>Pts</th></tr><tr>{cell("X", "X", ENG)}<td>12.000</td></tr></table>"""


ASSOCIATIONS = f"""<table><tr><th>Rank</th><th>Association</th><th>Coeff.</th></tr>
<tr><td>1</td><td>{plain_flag()} <a rel="mw:WikiLink" href="{W}The_Football_Association" title="The Football Association">England</a></td><td>109.570</td></tr>
<tr><td>20</td><td>{plain_flag()} <a rel="mw:WikiLink" href="{W}{TFF}" title="Turkish Football Federation">Turkey</a></td><td>36.000</td></tr>
</table>"""


def test_coefficient_table_with_two_pairs_per_row():
    assert p.parse_coefficients(COEFFS) == [
        p.Coefficient("Burnley F.C.", "Burnley", "The Football Association", 15.921),
        p.Coefficient("S.L. Benfica", "Benfica", "Portuguese Football Federation", 80.0),
    ]


def test_association_ranking_rows():
    rows = p.parse_coefficients(ASSOCIATIONS)
    assert [(r.title, r.name, r.is_club, r.value) for r in rows] == [
        ("The Football Association", "England", False, 109.57),
        ("Turkish Football Federation", "Turkey", False, 36.0),
    ]


def test_round_codes():
    assert round_code("2018–19 UEFA Europa League group stage", "Groups / Group J") == ("GS", "J")
    assert round_code("2024–25 UEFA Champions League league phase", "Matchday 1") == ("LP", None)
    page = "2018–19 UEFA Champions League qualifying"
    assert round_code(page, "Preliminary round / Semi-final round") == ("PR", None)
    assert round_code(page, "Third qualifying round / League Path matches") == ("Q3", None)
    assert round_code(page, "Play-off round / Champions Path matches") == ("PO", None)
    ko = "2022–23 UEFA Europa League knockout phase"
    assert round_code(ko, "Knockout round play-offs / Matches") == ("KPO", None)
    assert round_code(ko, "Quarter-finals / Matches") == ("QF", None)
    assert round_code(ko, "Final") == ("F", None)


def test_season_records_resolve_unlinked_teams_and_legs():
    leg1 = box(
        "2018-08-09",
        team("İstanbul_Başakşehir_F.K.", "İstanbul Başakşehir", TFF),
        "0–0",
        team("Burnley_F.C.", "Burnley", ENG, home=False),
        report=2025331,
    )
    leg2 = box(
        "2018-08-16",
        team(None, "Burnley", ENG),
        "1–0 (a.e.t.)",
        team(None, "İstanbul Başakşehir", TFF, home=False),
        hgoals=f"<ul>{goal(97)}</ul>",
    )
    page = Article(
        "2018–19 UEFA Europa League qualifying",
        "<h2>Third qualifying round</h2>"
        + ASSOCIATIONS
        + COEFFS
        + leg1
        + leg2
        + leg2,  # leg 2 twice
    )
    data = collect_season("2018-19", {"UEL": [page]}, {"İstanbul Başakşehir F.K.": 5641})
    assert data.issues == []
    assert data.associations["The Football Association"] == ("England", 109.57)
    assert "The Football Association" not in data.coefficients
    first, second = data.matches
    assert (first.leg, second.leg) == (1, 2)
    assert second.opponent == "Burnley F.C." and second.opponent_coefficient == 15.921
    assert (second.team_id, second.tr_home) == (5641, False)
    assert (second.home_goals, second.away_goals, second.et_home, second.et_away) == (0, 0, 1, 0)
    assert check_season(data) == []


def test_missing_leg_is_reported():
    leg1 = box(
        "2018-08-09", team("T", "T", TFF), "0–0", team("Burnley_F.C.", "Burnley", ENG, False)
    )
    data = collect_season(
        "2018-19",
        {
            "UEL": [
                Article(
                    "x qualifying", "<h2>Third qualifying round</h2>" + ASSOCIATIONS + COEFFS + leg1
                )
            ]
        },
        {"T": 1},
    )
    assert check_season(data) == ["UEL Q3: club 1 vs Burnley F.C.: 1 match(es)"]


def test_wiki_helpers():
    assert wiki_season("2018-19") == "2018–19"
    assert cache_key('A: "b"/c').name == "A%3A_%22b%22%2Fc.html.gz"
    html = (
        "<title>2018–19 UEFA Europa League qualifying - Wikipedia</title>"
        f'<a href="{W}2018%E2%80%9319_UEFA_Europa_League_group_stage#Group_A">x</a>'
        f'<a href="{W}2018–19_UEFA_Europa_League">self</a>'
        f'<a href="{W}2019–20_UEFA_Europa_League_group_stage">next season</a>'
    )
    assert page_title(html) == "2018–19 UEFA Europa League qualifying"
    assert sub_articles(html, "2018–19 UEFA Europa League") == [
        "2018–19 UEFA Europa League group stage"
    ]
