"""Club display names, slugs and the website's data export."""

from datetime import date

from tlelo.elo.data import Dataset, Game, Side
from tlelo.elo.engine import Engine, EuropeModel
from tlelo.elo.params import V1
from tlelo.site.export import build
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
