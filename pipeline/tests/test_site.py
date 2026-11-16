"""Club display names, slugs and the website's data export."""

from datetime import date

from tlelo.elo.data import Dataset, Game, Side
from tlelo.elo.engine import Engine, EuropeModel
from tlelo.elo.params import V1
from tlelo.site.export import build, load_withdrawals
from tlelo.site.fixtures import stakes, upcoming
from tlelo.site.logos import logo_url, transparent_png
from tlelo.site.names import clean_name, slugify, tr_title, unique_slugs


def test_turkish_title_case():
    assert tr_title("İSTANBUL BAŞAKŞEHİR FK") == "İstanbul Başakşehir FK"
    assert tr_title("IĞDIR") == "Iğdır"  # dotless I stays dotless
    assert tr_title("MKE ANKARAGÜCÜ") == "MKE Ankaragücü"


def test_legal_forms_are_dropped():
    assert clean_name("GALATASARAY A.Ş.") == "Galatasaray"
    assert clean_name("GAZİANTEP FUTBOL KULÜBÜ A.Ş.") == "Gaziantep FK"
    assert clean_name("ESKİŞEHİRSPOR KULÜBÜ") == "Eskişehirspor"
    assert clean_name("ETİMESGUT SPOR KULÜBÜ") == "Etimesgut Spor"
    assert clean_name("7 EYLÜL TURGUTLU 1984 SPORTİF YATIRIMLAR A.Ş.") == "7 Eylül Turgutlu 1984"
    assert clean_name("NAZİLLİ SPOR A.Ş.") == "Nazilli Spor"
    assert clean_name("KIRIKKALE FK SPOR KULÜBÜ") == "Kırıkkale FK"


def test_slugs_are_ascii_and_unique():
    assert slugify("Şanlıurfaspor") == "sanliurfaspor"
    assert slugify("İstanbul Başakşehir FK") == "istanbul-basaksehir-fk"
    assert slugify("Kdz. Ereğli 1980 Spor") == "kdz-eregli-1980-spor"
    assert unique_slugs({1: "Hacettepe Spor", 2: "Hacettepe Spor", 3: "Altay"}) == {
        1: "hacettepe-spor-1",
        2: "hacettepe-spor-2",
        3: "altay",
    }


def _game(season, day, home, away, goals):
    h, a = goals
    return Game(
        key=f"{season}:{day}", season=season, date=date(int(season[:4]), 9, day), time="",
        competition="3L", stage="league", round=None, home=Side("pro", home, f"T{home}"),
        away=Side("pro", away, f"T{away}"), goals=goals, pens=None,
        result90="H" if h > a else "A" if h < a else "D", neutral=False,
        home_is_tr_venue=False, closed=False,
    )  # fmt: skip


def test_inactive_club_shows_the_rating_it_left_with(tmp_path):
    # Club 3 loses twice in 2021-22 and leaves; later anchor shifts still move its model
    # rating, but its page (header, chart, "unchanged since") shows the rating it left with.
    seasons = ["2020-21", "2021-22", "2022-23", "2023-24"]
    tiers = {s: {1: 4, 2: 4, 3: 4} for s in seasons[:2]} | {s: {1: 4, 2: 4} for s in seasons[2:]}
    games = {s: [] for s in seasons}
    games["2021-22"] = [_game("2021-22", 1, 1, 3, (2, 0)), _game("2021-22", 8, 2, 3, (1, 0))]
    games["2022-23"] = [_game("2022-23", 1, 1, 2, (1, 1))]
    games["2023-24"] = [_game("2023-24", 1, 2, 1, (2, 1))]
    data = Dataset(seasons, games, tiers, names={t: f"T{t}" for t in (1, 2, 3)})
    res = Engine(data, V1, EuropeModel(a=1000.0, b=150.0, home=70.0)).run()
    (tmp_path / "team_seasons.csv").write_text("team_id,season,group\n", encoding="utf-8")

    built = build(res, data, tmp_path)
    summary = {s["id"]: s for s in built["teams"]}
    for tm in built["details"].values():
        assert summary[tm.id]["rating"] == tm.events[-1]["ra"]  # header = end of the chart
    gone = summary[3]
    assert not gone["active"] and gone["week"] == 0 and gone["rank"] is None
    assert gone["rating"] != round(res.ratings[3], 1)  # the silent shift did happen


def test_withdrawal_is_a_trailing_run_of_lost_forfeits(tmp_path):
    lines = [
        "competition,date,home_id,away_id,home_goals,away_goals,status",
        "3L,2026-09-06,9,1,0,2,played",
        "3L,2026-09-13,8,9,3,0,forfeit",  # 8 wins; 9's run of lost forfeits starts
        "3L,2026-09-20,9,2,0,3,forfeit",
        "3L,2026-09-27,3,9,3,0,forfeit",
        "3L,2026-10-04,7,8,0,3,forfeit",  # 7: a single forfeit, then it plays again
        "3L,2026-10-11,7,1,1,1,played",
        "3L,2026-10-18,9,4,,,not_played",
    ]
    path = tmp_path / "2026-27.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert load_withdrawals(path) == {9: date(2026, 9, 13)}


def test_logo_url_from_a_club_page():
    page = (
        '<img id="ctl00_MPane_m_28_190_ctnr_m_28_190_dtKulupBilgisi_ad" '
        r'src="https://fys.tff.org/TFFUploadFolder/KulupLogolari\000158_120x120.png" />'
    )
    assert logo_url(page) == "https://fys.tff.org/TFFUploadFolder/KulupLogolari/000158_120x120.png"
    assert logo_url("<html><img src='/x.png'></html>") is None


def test_logo_background_becomes_transparent_but_white_inside_the_crest_stays(tmp_path):
    from PIL import Image

    img = Image.new("RGB", (40, 40), "white")  # JPEG-style white background
    for x in range(10, 30):
        for y in range(10, 30):
            img.putpixel((x, y), (20, 40, 120))  # the crest
    for x in range(16, 24):
        for y in range(16, 24):
            img.putpixel((x, y), (255, 255, 255))  # white inside the crest
    src, dst = tmp_path / "logo.jpg", tmp_path / "logo.png"
    img.save(src, quality=95)
    transparent_png(src, dst)
    out = Image.open(dst)
    assert out.getpixel((0, 0))[3] == 0  # background gone
    assert out.getpixel((12, 12))[3] == 255  # crest kept
    assert out.getpixel((20, 20))[3] == 255  # enclosed white kept


def test_white_inside_a_crest_stays_where_its_outline_has_a_gap(tmp_path):
    from PIL import Image

    img = Image.new("RGB", (40, 40), "white")
    for x in range(8, 32):
        for y in range(8, 32):
            outline = not (11 <= x < 29 and 11 <= y < 29)
            gap = x < 11 and 18 <= y < 20  # a 2 px break joins the inside to the background
            if outline and not gap:
                img.putpixel((x, y), (20, 40, 120))
    src, dst = tmp_path / "logo.jpg", tmp_path / "logo.png"
    img.save(src, quality=95)
    transparent_png(src, dst)
    out = Image.open(dst)
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((20, 20))[3] == 255


def test_a_black_ground_goes_too_but_black_inside_the_crest_stays(tmp_path):
    from PIL import Image

    img = Image.new("RGB", (40, 40), "black")
    for x in range(8, 32):
        for y in range(8, 32):
            if not (11 <= x < 29 and 11 <= y < 29):
                img.putpixel((x, y), (255, 255, 255))  # a white ring, black inside
    src, dst = tmp_path / "logo.jpg", tmp_path / "logo.png"
    img.save(src, quality=95)
    transparent_png(src, dst)
    out = Image.open(dst)
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((9, 20))[3] == 255  # the ring
    assert out.getpixel((20, 20))[3] == 255  # black inside the ring


def test_a_graded_grey_ground_goes_end_to_end(tmp_path):
    from PIL import Image

    img = Image.new("RGB", (40, 40))
    for x in range(40):
        for y in range(40):
            v = 255 - 65 * (x + y) // 78  # white in one corner, grey (190) in the other
            img.putpixel((x, y), (v, v, v))
    for x in range(14, 26):
        for y in range(14, 26):
            img.putpixel((x, y), (20, 40, 120))
    src, dst = tmp_path / "logo.jpg", tmp_path / "logo.png"
    img.save(src, quality=95)
    transparent_png(src, dst)
    out = Image.open(dst)
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((39, 39))[3] == 0
    assert out.getpixel((20, 20))[3] == 255


def test_a_logo_that_comes_cut_out_is_kept_as_it_is(tmp_path):
    from PIL import Image

    img = Image.new("RGBA", (40, 40), (255, 255, 255, 0))  # transparent, white underneath
    for x in range(10, 30):
        for y in range(10, 30):
            img.putpixel((x, y), (255, 255, 255, 255))  # white part of the crest at its edge
    for x in range(10, 30):
        img.putpixel((x, 20), (20, 40, 120, 255))
    src, dst = tmp_path / "logo.png", tmp_path / "out.png"
    img.save(src)
    transparent_png(src, dst)
    out = Image.open(dst)
    assert out.getpixel((0, 0))[3] == 0
    assert out.getpixel((15, 15))[3] == 255


def test_next_round_skips_leftovers_withdrawn_clubs_and_past_cup_ties():
    def row(comp, week, d, home, away, status, rnd=""):
        return {"competition": comp, "stage": "league" if comp == "SL" else "cup", "group": "",
                "week": week, "date": d, "time": "", "round": rnd, "home_id": str(home),
                "away_id": str(away), "status": status}  # fmt: skip

    rows = [
        row("SL", "1", "2026-08-10", 1, 2, "played"),
        row("SL", "2", "", 3, 4, "not_played"),  # postponed: before the last week with a result
        row("SL", "3", "2026-08-24", 2, 3, "played"),
        row("SL", "4", "", 1, 3, "not_played"),  # the next round
        row("SL", "4", "", 9, 2, "not_played"),  # 9 has withdrawn
        row("SL", "5", "", 1, 2, "not_played"),
        row("TK", "", "2026-08-20", 1, 4, "not_played", "1.Tur"),  # in the past: left over
        row("TK", "", "2026-09-02", 2, 4, "not_played", "2.Tur"),
    ]
    rounds, cup = upcoming(rows, date(2026, 8, 30), skip={9})
    week, matches = rounds[("SL", "")]
    assert week == 4 and [(m["home_id"], m["away_id"]) for m in matches] == [("1", "3")]
    assert [m["round"] for m in cup] == ["2.Tur"]


def test_stakes_mirror_between_the_two_sides():
    home, away = stakes(24, 1.0, 0.75), stakes(24, 1.0, 0.25)
    assert home == [6.0, -6.0, -18.0] and away == [18.0, 6.0, -6.0]


def test_every_european_opponents_association_has_a_country_code():
    import csv

    from tlelo import paths
    from tlelo.site.export import load_codes

    codes = load_codes(paths.data_dir() / "sources" / "association_codes.csv")
    with (paths.data_dir() / "europe" / "matches.csv").open(encoding="utf-8", newline="") as fh:
        used = {r[f"{side}_assoc"] for r in csv.DictReader(fh) for side in ("home", "away")}
    assert used - {"Turkish Football Federation"} - codes.keys() == set()
    assert all(len(c) == 3 and c.isupper() for c in codes.values())
