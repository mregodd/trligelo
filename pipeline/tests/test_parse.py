"""Parser tests on trimmed snippets of real tff.org markup (source: tff.org)."""

from datetime import date

from tlelo.http import cache_key
from tlelo.tff import parse as p

# --- helpers -----------------------------------------------------------------------------


def test_parse_score():
    assert p.parse_score("1 - 0") == (1, 0)
    assert p.parse_score("2-3") == (2, 3)
    assert p.parse_score(" - ") is None
    assert p.parse_score("") is None


def test_normalize_group_variants_compare_equal():
    assert p.normalize_group("01") == p.normalize_group("01 Grup") == "1"
    assert p.normalize_group("1. Grup Grup") == "1"
    assert p.normalize_group("Kırmızı") == p.normalize_group("KIRMIZI GRUP") == "kirmizi"
    assert p.normalize_group("A Grubu") == p.normalize_group("A") == "a"


def test_cache_key_is_stable_and_ordered():
    assert str(cache_key({"pageID": 1416, "hafta": 5, "grupID": 1356}).as_posix()) == (
        "p1416/grupID-1356_hafta-5.html.gz"
    )
    assert cache_key({"pageID": 1413}).as_posix() == "p1413/index.html.gz"


# --- fixture list ------------------------------------------------------------------------

FIXTURE = """
<span style="display:inline-block;font-size:11pt;font-weight:bold;height:50px;width:100%;">
Spor Toto 3.Lig<br/>01 Grup<br/>Sezon 2016-2017<br/><br/></span>
<table class="genelBorder fiksturListesiTable"><tr><td><table class="softBG"><tr>
<td class="belirginYazi" align="Center" style="font-size:9px;" nowrap="nowrap">1.Hafta</td></tr>
<tr><td><table><tr>
<td class="altCizgi" style="font-size:9px;"><a href="/Default.aspx?pageID=28&kulupId=44">SİLİVRİSPOR</a></td>
<td align="Justify" class="altCizgi" nowrap="nowrap" style="font-size:9px;"><a href="/Default.aspx?pageID=29&macId=211334">0 - 1</a></td>
<td align="Right" style="font-size:9px;" class="altCizgi"><a href="/Default.aspx?pageID=28&kulupId=4258">ERZİN SPOR A.Ş.</a></td>
</tr></table></td></tr></table>
<table class="softBG"><tr>
<td class="belirginYazi" align="Center" style="font-size:9px;" nowrap="nowrap">2.Hafta</td></tr>
<tr><td><table><tr>
<td class="altCizgi" style="font-size:9px;"><a href="/Default.aspx?pageID=28&kulupId=442">ŞİLE YILDIZSPOR</a></td>
<td align="Justify" class="altCizgi" nowrap="nowrap" style="font-size:9px;"><a href="/Default.aspx?pageID=29&macId=211586"> - </a></td>
<td align="Right" style="font-size:9px;" class="altCizgi"><a href="/Default.aspx?pageID=28&kulupId=4122">KIZILCABÖLÜKSPOR</a></td>
</tr></table></td></tr></table></td></tr></table>
<span style="display:inline-block;font-size:11pt;font-weight:bold;height:50px;width:100%;">
Spor Toto 3.Lig<br/>02 Grup<br/>Sezon 2016-2017<br/><br/></span>
<table class="genelBorder fiksturListesiTable"><tr><td><table class="softBG"><tr>
<td class="belirginYazi" align="Center" style="font-size:9px;" nowrap="nowrap">1.Hafta</td></tr>
<tr><td><table><tr>
<td class="altCizgi" style="font-size:9px;"><a href="/Default.aspx?pageID=28&amp;kulupId=3591">ALTAY</a></td>
<td align="Justify" class="altCizgi" nowrap="nowrap" style="font-size:9px;"><a href="/Default.aspx?pageID=29&amp;macId=159703">6 - 1</a></td>
<td align="Right" style="font-size:9px;" class="altCizgi"><a href="/Default.aspx?pageID=28&amp;kulupId=3614">BEYLERBEYİSPOR</a></td>
</tr></table></td></tr></table></td></tr></table>
"""


def test_parse_fixture_rows_weeks_and_groups():
    rows = {r.match_id: r for r in p.parse_fixture(FIXTURE)}
    assert set(rows) == {211334, 211586, 159703}

    played = rows[211334]
    assert (played.week, played.table_group) == (1, "1")
    assert (played.home_id, played.home_name) == (44, "SİLİVRİSPOR")
    assert (played.away_id, played.away_name, played.score) == (4258, "ERZİN SPOR A.Ş.", (0, 1))

    assert rows[211586].week == 2 and rows[211586].score is None  # not played
    assert rows[159703].table_group == "2" and rows[159703].score == (6, 1)


def test_rows_for_group_picks_the_requested_table():
    rows = p.parse_fixture(FIXTURE)
    assert {r.match_id for r in p.rows_for_group(rows, "02")} == {159703}
    assert {r.match_id for r in p.rows_for_group(rows, "01")} == {211334, 211586}
    assert p.rows_for_group(rows, "03") == []  # never borrow another group's table
    only_first = [r for r in rows if r.table_group == "1"]
    assert p.rows_for_group(only_first, "02") == []


def test_parse_groups():
    html = """
    <a href="Default.aspx?pageID=1415&grupID=1354#grp"> Beyaz </a>
    <a href="Default.aspx?pageID=1415&grupID=1354#hmac"> Beyaz </a>
    <a href="Default.aspx?pageID=1415&grupID=1355#grp"> Kırmızı </a>
    """
    assert p.parse_groups(html) == {1354: "Beyaz", 1355: "Kırmızı"}


# --- week views --------------------------------------------------------------------------

WEEK_SINGLE_TABLE = """
<tr class="haftaninMaclariTr"> <td align="left" class="haftaninMaclariTarih"> <b>
<span id="x_lblTarih">02.06.2017</span> <span id="x_lblSaat">17:00</span> </b> </td>
<td align="right" class="haftaninMaclariEv"> <a href="Default.aspx?pageId=28&kulupID=3606" id="x_A2">
<span id="x_Label4">GENÇLERBİRLİĞİ</span></a> </td>
<td align="center" class="haftaninMaclariSkor"> <b><a href="Default.aspx?pageId=29&macId=157223" id="x_A3">
<span id="x_Label5">1</span> - <span id="x_Label6">0</span></a> </td>
<td class="haftaninMaclariDeplasman"> <a href="Default.aspx?pageId=28&kulupID=39" id="x_A5">
<span id="x_Label1">KASIMPAŞA A.Ş.</span></a> </td> </tr>
<tr class="haftaninMaclariTr"> <td align="left" class="haftaninMaclariTarih"> <b>
<span id="y_lblTarih">19.04.2023</span> <span id="y_lblSaat"></span> </b> </td>
<td align="right" class="haftaninMaclariEv"> <a href="Default.aspx?pageId=28&kulupID=3590">
<span>BEŞİKTAŞ A.Ş.</span></a> </td>
<td align="center" class="haftaninMaclariSkor"> <b><a href="Default.aspx?pageId=29&macId=234975">
<span>3</span> - <span>0</span></a> </td>
<td class="haftaninMaclariDeplasman"> <a href="Default.aspx?pageId=28&kulupID=3663">
<span>ATAKAŞ HATAYSPOR</span></a> </td> </tr>
"""

WEEK_GROUPED = """
<tr align="left"> <td class="altGriCizgi" style="width:170px;"> <b>
<span id="z_lblTarih">01.10.2016</span>&nbsp;<span id="z_lbSaat">13:30</span> </b> </td>
<td class="altGriCizgi" align="right"> <a href="Default.aspx?pageID=28&amp;kulupID=778">SANCAKTEPE BELEDİYE SPOR</a> </td>
<td class="altGriCizgi" align="center" style="white-space:nowrap;">
<a href="Default.aspx?pageID=29&amp;macId=159412" style="font-weight:bold;">2-0</a> </td>
<td class="altGriCizgi" align="left"> <a href="Default.aspx?pageID=28&amp;kulupID=2035">24ERZİNCANSPOR</a> </td>
<td class="altGriCizgi"> <a href="Default.aspx?pageId=29&macId=159412"><img alt="Detaylar"></a></td> </tr>
<tr> <td class="altCizgi"><a href="/Default.aspx?pageID=28&kulupId=1">NO DATE ROW</a></td>
<td><a href="/Default.aspx?pageID=29&macId=999">1 - 1</a></td>
<td><a href="/Default.aspx?pageID=28&kulupId=2">OTHER</a></td></tr>
"""


def test_week_dates_single_table_layout_and_forfeit_without_time():
    rows = p.parse_week_dates(WEEK_SINGLE_TABLE)
    assert rows[157223].date == date(2017, 6, 2) and rows[157223].time == "17:00"
    assert rows[157223].score == (1, 0)
    assert (rows[157223].home_name, rows[157223].away_id) == ("GENÇLERBİRLİĞİ", 39)
    forfeit = rows[234975]
    assert forfeit.date == date(2023, 4, 19) and forfeit.time is None and forfeit.score == (3, 0)


def test_week_dates_grouped_layout_ignores_undated_rows():
    rows = p.parse_week_dates(WEEK_GROUPED)
    assert set(rows) == {159412}
    row = rows[159412]
    assert (row.date, row.time, row.score) == (date(2016, 10, 1), "13:30", (2, 0))
    assert (row.home_id, row.away_name) == (778, "24ERZİNCANSPOR")


def test_parse_week_links():
    html = '<a href=Default.aspx?pageID=1416&hafta=10#grp>10</a><a href="x?pageID=1&amp;hafta=2">'
    assert p.parse_week_links(html) == [2, 10]


# --- cup rounds / play-offs --------------------------------------------------------------

CUP = """
<tr> <td class="alanTurkiyeKupasi" style="width: 100%;" colspan="5"> <b> <span id="h1">Final Maçları</span> </b> </td></tr>
<tr align="center"> <td style="white-space: nowrap; text-align: right;"> <b> <span id="d1">14 Mayıs 2017 15:00</span> </b> </td>
<td> <a href="Default.aspx?pageID=28&amp;kulupID=3594">SAKARYASPOR A.Ş.</a> </td>
<td nowrap> <a href="Default.aspx?pageID=29&amp;macId=179716" style="font-weight:bold;">0-0</a>
<div style="color:#e30a17"> <span style="font-weight:bold;">(Uzt.</span> <span style="font-weight:bold;">2-1)</span> </div> </td>
<td> <a href="Default.aspx?pageID=28&amp;kulupID=3196">DİYARBEKİR SPOR A.Ş.</a> </td>
<td> <a href="Default.aspx?pageId=29&macId=179716"><img alt="Detaylar"></a> </td> </tr>
<tr> <td class="alanTurkiyeKupasi" style="width: 100%;" colspan="5"> <b> </b> </td></tr>
<tr align="center"> <td> <b> <span>31 Mayıs 2017 21:30</span> </b> </td>
<td> <a href="Default.aspx?pageID=28&amp;kulupID=3665">MEDİPOL BAŞAKŞEHİR FK</a> </td>
<td nowrap> <a href="Default.aspx?pageID=29&amp;macId=179922" style="font-weight:bold;">0-0</a>
<div> <span style="font-weight:bold;">(Pen. 1-4)</span> </div> </td>
<td> <a href="Default.aspx?pageID=28&amp;kulupID=3600">ATİKER KONYASPOR</a> </td> </tr>
<tr> <td class="alanTurkiyeKupasi" colspan="5"> <b> <span>3.Tur Maçları</span> </b> </td></tr>
<tr align="center"> <td> <b> <span>25 Ekim 2016 12:00</span> </b> </td>
<td> <a href="Default.aspx?pageID=28&amp;kulupID=1">PENDİKSPOR</a> </td>
<td nowrap> <a href="Default.aspx?pageID=29&amp;macId=177242" style="font-weight:bold;">0-1</a> </td>
<td> <a href="Default.aspx?pageID=28&amp;kulupID=3606">GENÇLERBİRLİĞİ</a> </td> </tr>
"""


def test_cup_rows_extra_time_penalties_and_rounds():
    rows = {r.match_id: r for r in p.parse_cup_rows(CUP)}
    et = rows[179716]
    assert (et.round, et.date, et.time) == ("Final Maçları", date(2017, 5, 14), "15:00")
    assert (et.score, et.extra_time, et.penalties) == ((0, 0), (2, 1), None)

    pens = rows[179922]
    assert pens.round == "Final Maçları"  # empty header keeps the previous round
    assert (pens.score, pens.extra_time, pens.penalties) == ((0, 0), None, (1, 4))

    plain = rows[177242]
    assert plain.round == "3.Tur Maçları" and plain.date == date(2016, 10, 25)
    assert (plain.home_name, plain.penalties) == ("PENDİKSPOR", None)  # "Pen" in a name


# --- standings and match detail ----------------------------------------------------------

STANDINGS = """
<tr> <td class="griBG" style="white-space: nowrap;"> <b>
<a id="m_grvACetvel_ctl04_lnkTakim" href="Default.aspx?pageId=28&amp;kulupID=3604">4.GALATASARAY A.Ş.</a></b></td>
<td><span id="m_grvACetvel_ctl04_lblOyun">34</span></td> <td><span id="a">20</span></td>
<td><span id="b">4</span></td> <td><span id="c">10</span></td> <td><span id="d">65</span></td>
<td><span id="e">40</span></td> <td><span id="f">25</span></td> <td> <b> <span id="g">64</span></b></td> </tr>
"""


def test_parse_standings():
    assert p.parse_standings(STANDINGS) == [p.StandingRow(3604, 34, 20, 4, 10, 65, 40, 64)]


def test_match_detail_forfeit_has_no_officials():
    forfeit = """<a id="x_lnkStad" href="Default.aspx?pageId=394&amp;stadId=6097">VODAFONE PARK - İSTANBUL</a>
    <span id="x_lblTarih">19.04.2023 </span></b><br> <div class="dtMacBilgisiHakemler"> </div>"""
    normal = """<a id="x_lnkStad" href="Default.aspx?pageId=394&amp;stadId=110">ATATÜRK OLİMPİYAT - İSTANBUL</a>
    <div class="dtMacBilgisiHakemler"><a href="#">ALİ ŞANSALAN(Hakem)</a></div>"""
    d = p.parse_match_detail(1, forfeit)
    assert (d.venue_id, d.venue, d.has_officials) == (6097, "VODAFONE PARK - İSTANBUL", False)
    assert p.parse_match_detail(2, normal).has_officials is True
