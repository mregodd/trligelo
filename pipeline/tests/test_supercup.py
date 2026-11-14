"""Süper Kupa history table and detail-page parsing (snippets of real tff.org markup)."""

from datetime import date

from tlelo.tff.parse import parse_match_detail
from tlelo.tff.supercup import parse_history, season_of

HISTORY = """
<tr> <td><p>10.01.2026</p></td> <td><p><a><span>ATATÜRK OLİMPİYAT</span></a></p></td>
<td><p>GALATASARAY</p></td>
<td><p><a href="https://www.tff.org/Default.aspx?pageID=29&amp;macID=315426"><strong><span>0-2</span></strong></a></p></td>
<td><p><strong>FENERBAHÇE</strong></p></td> </tr>
<tr> <td><p>07.04.2024</p></td> <td><p>11 NİSAN STADYUMU</p></td> <td><p>GALATASARAY</p></td>
<td><p><a href="https://www.tff.org/Default.aspx?pageID=29&amp;macID=264343">3-0</a> (HÜKMEN)</p></td>
<td><p>FENERBAHÇE</p></td> </tr>
<tr> <td><p>13.08.2016</p></td> <td><p>KONYA B.Ş. BELEDİYE</p></td> <td><p>BEŞİKTAŞ A.Ş.</p></td>
<td><p><a href="https://www.tff.org/Default.aspx?pageID=29&amp;macID=160322">1 - 1</a> (0 - 3 P.)</p></td>
<td><p>GALATASARAY A.Ş.</p></td> </tr>
<tr> <td><p><strong>Tarih</strong></p></td> <td>Stat</td> <td>1. Takım</td> <td>Skor</td> <td>2. Takım</td> </tr>
"""


def test_parse_history_scores_penalties_and_forfeits():
    finals = {f.match_id: f for f in parse_history(HISTORY)}
    assert set(finals) == {315426, 264343, 160322}
    assert finals[315426].date == date(2026, 1, 10) and finals[315426].score == (0, 2)
    assert finals[264343].forfeit and finals[264343].score == (3, 0)
    shootout = finals[160322]
    assert (shootout.score, shootout.penalties, shootout.forfeit) == ((1, 1), (0, 3), False)


def test_season_of():
    assert season_of(date(2016, 8, 13)) == "2016-17"
    assert season_of(date(2026, 1, 10)) == "2025-26"
    assert season_of(date(2024, 4, 7)) == "2023-24"


def test_match_detail_teams_score_and_date():
    html = """
    <a id="x_MacBilgiDisplay1_dtMacBilgisi_lnkTakim1" href="Default.aspx?pageId=28&amp;kulupId=3604">GALATASARAY A.Ş.</a>
    <p class="MacDetaySayi"> <span id="x_MacBilgiDisplay1_dtMacBilgisi_lblTakim1Skor">0</span> </p>
    <p class="MacDetaySayi"> <span id="x_MacBilgiDisplay1_dtMacBilgisi_Label12">2</span> </p>
    <a id="x_MacBilgiDisplay1_dtMacBilgisi_lnkTakim2" href="Default.aspx?pageId=28&amp;kulupId=3592">FENERBAHÇE A.Ş.</a>
    <span id="x_MacBilgiDisplay1_dtMacBilgisi_lblTarih">10.01.2026 - 18:45</span>
    """
    d = parse_match_detail(315426, html)
    assert (d.home_id, d.home_name, d.away_id, d.away_name) == (
        3604,
        "GALATASARAY A.Ş.",
        3592,
        "FENERBAHÇE A.Ş.",
    )
    assert (d.score, d.date, d.time) == ((0, 2), date(2026, 1, 10), "18:45")
