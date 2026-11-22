"""Build the website's JSON from a model run (``uv run tlelo site``).

Output (``web/src/data/``, generated, not committed):

  meta.json            model version, update dates, display window, Europe model
  teams.json           one summary per club shown on the site (rank, rating, weekly change)
  leagues.json         the running season's leagues and groups, clubs in rating order
  teams/<slug>.json    one club's history in the display window: every match with the
                       numbers of its calculation, and every adjustment

Only the display window (2021-22 onward) is exported; earlier seasons are warm-up.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np

from tlelo.elo.backtest import arrays
from tlelo.elo.data import Dataset
from tlelo.elo.engine import RunResult, expected
from tlelo.elo.fit import OrderedLogit
from tlelo.elo.params import MODEL_VERSION
from tlelo.site.fixtures import LEAGUES, chances, load_rows, stakes, upcoming
from tlelo.site.logos import logo_path, transparent_png
from tlelo.site.names import clean_name, display_name, load_masked, load_overrides, unique_slugs

DISPLAY_FROM = "2021-22"
LEAGUE_CODES = {1: "SL", 2: "1L", 3: "2L", 4: "3L"}


@dataclass(slots=True)
class TeamOut:
    id: int
    slug: str
    name: str
    official: str
    events: list[dict] = field(default_factory=list)


def _r(x: float, nd: int = 1) -> float:
    return round(float(x), nd)


def visible_teams(data: Dataset) -> list[int]:
    """Clubs with a page on the site: every club in the display window."""
    return sorted({t for s in data.seasons if s >= DISPLAY_FROM for t in data.tiers.get(s, {})})


def load_groups(path: Path) -> dict[tuple[int, str], str]:
    with path.open(encoding="utf-8", newline="") as fh:
        return {(int(r["team_id"]), r["season"]): r["group"] for r in csv.DictReader(fh)}


def load_withdrawals(path: Path) -> dict[int, date]:
    """Clubs that left their league during the season, by TFF's own record: their last three
    or more league results are forfeits they lost, with nothing played after. Value: the
    date of the first of those forfeits."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["competition"] in LEAGUE_CODES.values()]
    rows = [r for r in rows if r["status"] != "not_played"]
    runs: dict[int, list[date]] = defaultdict(list)  # each club's trailing forfeit losses
    for r in sorted(rows, key=lambda r: r["date"]):
        for side, other in (("home", "away"), ("away", "home")):
            team = int(r[f"{side}_id"])
            lost = r["status"] == "double_forfeit" or (
                r["status"] == "forfeit" and int(r[f"{side}_goals"]) < int(r[f"{other}_goals"])
            )
            if lost:
                runs[team].append(date.fromisoformat(r["date"]))
            else:
                runs[team].clear()
    return {t: ds[0] for t, ds in runs.items() if len(ds) >= 3}


def load_codes(path: Path) -> dict[str, str]:
    """National associations (as Wikipedia names them) to FIFA country codes."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        return {r["association"]: r["code"] for r in csv.DictReader(fh)}


def _match_event(
    rec, is_home: bool, slugs: dict, names: dict, logo_urls: dict, codes: dict, masked: set
) -> dict:
    g = rec.game
    side, other = (g.home, g.away) if is_home else (g.away, g.home)
    h = rec.h if is_home else -rec.h
    gf, ga = g.goals if is_home else g.goals[::-1]
    pens = (g.pens if is_home else g.pens[::-1]) if g.pens else None
    opp: dict = {"kind": other.kind}
    if other.kind == "pro":
        slug = slugs.get(other.team)
        opp |= {"name": names[other.team], "slug": slug, "logo": logo_urls.get(slug)}
        if opp["logo"] is None and other.team not in masked:
            opp["country"] = "TUR"  # no logo: the country stands in, as for foreign clubs
    elif other.kind == "amateur":
        opp |= {"name": clean_name(other.name), "country": "TUR"}  # amateur clubs: no logos
    else:
        # No logo for foreign clubs (no freely licensed source): the site shows the country.
        opp |= {"name": other.name, "coef": other.coefficient, "country": codes.get(other.assoc)}
    return {
        "t": "match",
        "seq": rec.seq,
        "date": g.date.isoformat(),
        "season": g.season,
        "comp": g.competition,
        "round": g.round,
        "venue": "n" if h == 0 else ("h" if h > 0 else "a"),
        "opp": opp,
        "gf": gf,
        "ga": ga,
        "g90": (list(g.goals90) if is_home else list(g.goals90[::-1])) if g.goals90 else None,
        "pens": list(pens) if pens else None,
        "r": _r(rec.r_home if is_home else rec.r_away),
        "ro": _r(rec.r_away if is_home else rec.r_home),
        "h": _r(h) + 0.0,
        "e": round(rec.expected if is_home else 1 - rec.expected, 4),
        "s": g.score if is_home else 1 - g.score,
        "k": _r(rec.k_home if is_home else rec.k_away, 2),
        "w": rec.weight,
        "g": rec.margin,
        "d": _r(rec.delta_home if is_home else rec.delta_away, 2),
        "ra": _r((rec.r_home + rec.delta_home) if is_home else (rec.r_away + rec.delta_away)),
    }


def build(res: RunResult, data: Dataset, data_dir: Path) -> dict:
    overrides = load_overrides(data_dir / "sources" / "team_display_names.csv")
    masked = load_masked(data_dir / "sources" / "team_display_names.csv")
    codes = load_codes(data_dir / "sources" / "association_codes.csv")
    groups = load_groups(data_dir / "team_seasons.csv")
    window = [s for s in data.seasons if s >= DISPLAY_FROM]
    current = data.seasons[-1]
    withdrawn = load_withdrawals(data_dir / "matches" / f"{current}.csv")
    p = res.params
    visible = visible_teams(data)
    names = {t: display_name(t, data.names[t], overrides) for t in data.names}
    slugs = unique_slugs({t: names[t] for t in visible})
    logos = {slugs[t]: f for t in visible
             if t not in masked and (f := logo_path(data_dir / "raw" / "tff", t))}  # fmt: skip
    logo_urls = {slug: f"/logos/{slug}.png" for slug in logos}  # see write_logos

    teams = {t: TeamOut(t, slugs[t], names[t], "" if t in masked else data.names[t])
             for t in visible}  # fmt: skip
    first_game = {s: gs[0].date for s, gs in data.games.items() if gs}
    for rec in res.records:
        if rec.game.season not in window:
            continue
        for is_home in (True, False):
            side = rec.game.home if is_home else rec.game.away
            if side.kind == "pro" and side.team in teams:
                event = _match_event(rec, is_home, slugs, names, logo_urls, codes, masked)
                teams[side.team].events.append(event)
    for adj in res.adjustments:
        if adj.season not in window or adj.team not in teams or adj.kind == "seed":
            continue
        when = adj.date or first_game.get(adj.season)
        teams[adj.team].events.append({
            "t": adj.kind, "seq": adj.seq, "date": when.isoformat() if when else None,
            "season": adj.season, "d": _r(adj.delta, 2), "ra": _r(adj.rating),
        })  # fmt: skip
    for team in teams.values():
        team.events.sort(key=lambda e: e["seq"])

    last_match = max(r.game.date for r in res.records)
    cutoff = last_match - timedelta(days=7)
    tiers_now = data.tiers[current]
    active = sorted((t for t in visible if t in tiers_now and t not in withdrawn),
                    key=lambda t: -res.ratings[t])  # fmt: skip
    rank = {t: i for i, t in enumerate(active, start=1)}
    league_rank: dict[int, int] = {}
    by_league: dict[int, list[int]] = defaultdict(list)
    for t in active:
        by_league[tiers_now[t]].append(t)
    for teams_in in by_league.values():
        for i, t in enumerate(teams_in, start=1):
            league_rank[t] = i

    # Places gained over the same week: in the ranking, and in each group as league pages show it.
    start = {t: _week_start(teams[t].events, res.ratings[t], cutoff) for t in active}
    move = _moves(active, start)
    group_move: dict[int, int] = {}
    for members in by_league.values():
        in_group: dict[str, list[int]] = defaultdict(list)
        for t in members:
            in_group[groups.get((t, current), "")].append(t)
        for ts in in_group.values():
            group_move |= _moves(ts, start)

    summaries = []
    for t in visible:
        tm = teams[t]
        last_season = max(s for s in window if t in data.tiers.get(s, {}))
        tier = data.tiers[last_season][t]
        # Inactive clubs show the rating they left with: later anchor shifts move them silently.
        r = res.ratings[t] if t in rank else tm.events[-1]["ra"]
        summary = _summary(tm, r, last_season, tier, groups, rank, league_rank, cutoff,
                           withdrawn.get(t))  # fmt: skip
        summary["logo"] = logo_urls.get(tm.slug)
        summary["move"], summary["groupMove"] = move.get(t), group_move.get(t)
        summaries.append(summary)

    leagues = []
    for tier in (1, 2, 3, 4):
        members = by_league[tier]
        by_group: dict[str, list[int]] = defaultdict(list)
        for t in members:
            by_group[groups.get((t, current), "")].append(t)
        leagues.append({
            "code": LEAGUE_CODES[tier],
            "groups": [{"name": g or None, "teams": [slugs[t] for t in ts]}
                       for g, ts in sorted(by_group.items())],
        })  # fmt: skip

    ol = OrderedLogit.fit(*arrays(res, window)[:2])
    meta = {
        "model": MODEL_VERSION,
        "generatedAt": datetime.now(UTC).isoformat(timespec="seconds"),
        "lastMatch": last_match.isoformat(),
        "weekFrom": (cutoff + timedelta(days=1)).isoformat(),
        "season": current,
        "displayFrom": DISPLAY_FROM,
        "activeTeams": len(active),
        "teams": len(visible),
        "europe": {"a": _r(res.europe.a), "b": _r(res.europe.b), "home": _r(res.europe.home)},
        # The numbers the site's explanations quote, so they follow the model version.
        "params": {
            "k": p.k, "provisionalFactor": p.provisional_factor,
            "provisionalGames": p.provisional_games, "homeClosed": p.home_closed,
            "regression": p.regression, "newcomer": p.newcomer, "anchor": p.anchor,
        },
        # Win / draw / loss chances from the rating difference (the backtest's ordered logit,
        # fitted on the displayed seasons): the match explanations quote them.
        "outcome": {"beta": round(ol.beta, 5), "c1": round(ol.c1, 5), "c2": round(ol.c2, 5)},
    }  # fmt: skip
    # Upcoming matches: each league group's next round, dated cup ties, and per club its next.
    rounds, cup = upcoming(load_rows(data_dir / "matches" / f"{current}.csv"), last_match,
                           set(withdrawn))  # fmt: skip
    side_of = {t: {"slug": slugs[t], "name": names[t], "logo": logo_urls.get(slugs[t])}
               for t in visible}  # fmt: skip
    order = sorted(rounds, key=lambda k: (LEAGUES.index(k[0]), k[1]))

    def matches(rows: list[dict]) -> list[dict]:
        return [m for r in rows if (m := _fixture(r, side_of, ol, res))]

    fixtures = {
        "rounds": [{"league": comp, "group": g or None, "week": rounds[(comp, g)][0],
                    "matches": matches(rounds[(comp, g)][1])} for comp, g in order],
        "cup": matches(cup),
    }  # fmt: skip
    next_of: dict[str, list[dict]] = defaultdict(list)
    for m in [m for rnd in fixtures["rounds"] for m in rnd["matches"]] + fixtures["cup"]:
        for side in ("home", "away"):
            mine = next_of[m[side]["slug"]]
            if not any(x["comp"] == m["comp"] for x in mine):  # one league match, one cup tie
                mine.append(m)

    seasons = {
        t: [
            {
                "season": s,
                "league": LEAGUE_CODES[data.tiers[s][t]],
                "group": groups.get((t, s)) or None,
            }
            for s in window
            if t in data.tiers.get(s, {})
        ]
        for t in visible
    }
    return {
        "meta": meta, "teams": summaries, "leagues": leagues, "details": teams, "seasons": seasons,
        "logos": logos, "fixtures": fixtures, "next": next_of,
    }  # fmt: skip


def _fixture(row: dict, side_of: dict, ol: OrderedLogit, res: RunResult) -> dict | None:
    """One upcoming match between two clubs of the site: chances and what each result is worth."""
    home, away = int(row["home_id"]), int(row["away_id"])
    if home not in side_of or away not in side_of:
        return None  # an amateur club or one outside the display window (cup ties)
    p = res.params
    rh, ra = res.ratings[home], res.ratings[away]
    lead = rh + p.home - ra
    e = expected(lead)
    w = {"TK": p.w_cup_final if row["round"].startswith("Final") else p.w_cup,
         "SK": p.w_supercup}.get(row["competition"], p.w_league)  # fmt: skip
    pa, pd, ph = ol.probabilities(np.array([lead]))[0]
    return {
        "date": row["date"] or None, "time": row["time"] or None, "comp": row["competition"],
        "week": int(row["week"]) if row["week"] else None, "round": row["round"] or None,
        "home": side_of[home] | {"r": _r(rh)}, "away": side_of[away] | {"r": _r(ra)},
        "h": p.home, "p": chances(pa, pd, ph),
        "stakes": {"home": stakes(res.k_next[home], w, e),
                   "away": stakes(res.k_next[away], w, 1 - e)},
    }  # fmt: skip


def _week_start(events: list[dict], rating: float, cutoff: date) -> float:
    """A club's rating at the start of the week the site shows changes for."""
    before = [e for e in events if e["date"] and date.fromisoformat(e["date"]) <= cutoff]
    return before[-1]["ra"] if before else (events[0]["ra"] - events[0]["d"] if events else rating)


def _moves(now: list[int], start: dict[int, float]) -> dict[int, int]:
    """Places each club gained (+) or lost (-) since the week started; `now` is best first."""
    before = {t: i for i, t in enumerate(sorted(now, key=lambda t: -start[t]))}
    return {t: before[t] - i for i, t in enumerate(now)}


def _summary(tm, rating, last_season, tier, groups, rank, league_rank, cutoff, withdrawn):
    events = tm.events
    matches = [e for e in events if e["t"] == "match"]
    week_start = _week_start(events, rating, cutoff)
    peak = max(events, key=lambda e: e["ra"]) if events else None
    low = min(events, key=lambda e: e["ra"]) if events else None
    form = [{"s": e["s"], "d": e["d"]} for e in matches[-5:]]
    return {
        "id": tm.id, "slug": tm.slug, "name": tm.name, "official": tm.official,
        "active": tm.id in rank,
        "withdrawn": withdrawn.isoformat() if withdrawn else None,
        "league": LEAGUE_CODES[tier], "group": groups.get((tm.id, last_season)) or None,
        "lastSeason": last_season,
        "rating": _r(rating), "rank": rank.get(tm.id), "leagueRank": league_rank.get(tm.id),
        "week": _r(rating - week_start, 1) + 0.0,
        "games": len(matches),
        "peak": {"r": peak["ra"], "date": peak["date"]} if peak else None,
        "low": {"r": low["ra"], "date": low["date"]} if low else None,
        "form": form,
    }  # fmt: skip


def write(out_dir: Path, built: dict) -> int:
    (out_dir / "teams").mkdir(parents=True, exist_ok=True)
    for old in (out_dir / "teams").glob("*.json"):
        old.unlink()

    def dump(path: Path, obj) -> None:
        path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")),
                        encoding="utf-8")  # fmt: skip

    dump(out_dir / "meta.json", built["meta"])
    dump(out_dir / "teams.json", built["teams"])
    dump(out_dir / "leagues.json", built["leagues"])
    dump(out_dir / "fixtures.json", built["fixtures"])
    summaries = {s["slug"]: s for s in built["teams"]}
    for tm in built["details"].values():
        detail = {**summaries[tm.slug], "seasons": built["seasons"][tm.id],
                  "next": built["next"].get(tm.slug, []), "events": tm.events}  # fmt: skip
        dump(out_dir / "teams" / f"{tm.slug}.json", detail)
    return len(built["details"])


def write_logos(out_dir: Path, built: dict) -> int:
    """The cached logos, background removed, into the website (``web/public/logos/<slug>.png``)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.iterdir():
        old.unlink()
    for slug, src in built["logos"].items():
        transparent_png(src, out_dir / f"{slug}.png")
    return len(built["logos"])
