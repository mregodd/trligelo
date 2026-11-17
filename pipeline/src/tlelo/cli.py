"""Command line entry point: ``uv run tlelo <command>``.

Commands:
    fetch     download season, group and week pages into the cache
    details   download match detail pages (forfeit checks, play-off / final venues)
    build     write data/matches/*.csv and the team tables from the cache
    validate  compare parsed matches with TFF's standings tables
    europe-fetch  download the Wikipedia articles of the UEFA competitions
    europe-build  write data/europe/*.csv (Turkish clubs' UEFA matches, club coefficients)
    europe-check  list unresolved clubs, missing coefficients and incomplete ties
    elo       compute the ratings (model v1.0) into data/ratings/
    backtest  recompute the backtest report (docs/backtest.md)
    site      write the website's JSON data (web/src/data/) and copy the club logos
    logos     download the logos of the site's clubs from their TFF pages into the cache
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from tlelo import paths
from tlelo.build import write_europe, write_matches, write_teams
from tlelo.europe import wiki
from tlelo.europe.collect import SeasonData, collect_season, load_tr_clubs
from tlelo.europe.validate import check_season
from tlelo.http import MissingPage, PoliteClient
from tlelo.tff.collect import (
    CompetitionData,
    apply_overrides,
    collect_competition,
    fetch_details,
    load_overrides,
)
from tlelo.tff.crawl import CompetitionPage, fetch_competition, load_pages
from tlelo.tff.supercup import collect_supercup, fetch_supercup
from tlelo.validate import check_competition

log = logging.getLogger("tlelo")
COMPETITIONS = ["SL", "1L", "2L", "3L", "TK", "SK"]


def _selected(args: argparse.Namespace) -> list[CompetitionPage]:
    pages = load_pages(paths.tff_pages_csv())
    if args.competition:
        pages = [p for p in pages if p.competition in args.competition]
    if args.season:
        pages = [p for p in pages if p.season in args.season]
    if args.current_only:
        pages = [p for p in pages if p.current]
    return pages


def _wants_supercup(args: argparse.Namespace) -> bool:
    return not args.competition or "SK" in args.competition


def _supercup_extra():
    return paths.data_dir() / "sources" / "supercup_extra.csv"


def _collect_all(args: argparse.Namespace) -> list[CompetitionData]:
    out = _collect_raw(args)
    overrides = load_overrides(paths.data_dir() / "sources" / "match_overrides.csv")
    for data in out:
        apply_overrides(data, overrides)
    return out


def _collect_raw(args: argparse.Namespace) -> list[CompetitionData]:
    out = []
    with PoliteClient(paths.raw_cache_dir(), offline=True) as client:
        for page in _selected(args):
            try:
                out.append(collect_competition(client, page))
            except MissingPage as exc:
                log.warning("%s: not downloaded yet (%s)", page.label(), exc)
        if _wants_supercup(args):
            current = {p.season for p in load_pages(paths.tff_pages_csv()) if p.current}
            try:
                out += [
                    d
                    for d in collect_supercup(client, _supercup_extra())
                    if (not args.season or d.comp.season in args.season)
                    and (not args.current_only or d.comp.season in current)
                ]
            except MissingPage as exc:
                log.warning("SK: not downloaded yet (%s)", exc)
    return out


def cmd_fetch(args: argparse.Namespace) -> int:
    started = time.monotonic()
    with PoliteClient(paths.raw_cache_dir(), min_interval=args.interval) as client:
        for page in _selected(args):
            fetch_competition(client, page, refresh_current=args.refresh_current)
        if _wants_supercup(args):
            fetch_supercup(client, refresh=args.refresh_current)
        log.info(
            "fetch done in %.0f min: %s", (time.monotonic() - started) / 60, dict(client.stats)
        )
    return 0


def cmd_details(args: argparse.Namespace) -> int:
    started = time.monotonic()
    with PoliteClient(paths.raw_cache_dir(), min_interval=args.interval) as client:
        for page in _selected(args):
            fetch_details(client, page)
        log.info(
            "details done in %.0f min: %s", (time.monotonic() - started) / 60, dict(client.stats)
        )
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    data = _collect_all(args)
    counts = write_matches(paths.data_dir(), data)
    teams = write_teams(paths.data_dir())
    for season, n in counts.items():
        log.info("%s: %d matches", season, n)
    issues = sum(len(d.issues) for d in data)
    log.info("%d teams, %d issues (see `tlelo validate -v`)", teams, issues)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    data = _collect_all(args)
    bad = 0
    for comp in data:
        status = {}
        for m in comp.matches:
            status[m.status] = status.get(m.status, 0) + 1
        print(f"\n## {comp.comp.label()}: {len(comp.matches)} matches {status}")
        if args.verbose:
            for issue in comp.issues[:50]:
                print(f"   issue: {issue}")
            if len(comp.issues) > 50:
                print(f"   ... {len(comp.issues) - 50} more issues")
        elif comp.issues:
            print(f"   {len(comp.issues)} issues (use -v)")
        for check in check_competition(comp):
            mark = "OK " if not check.mismatches else "ERR"
            bad += bool(check.mismatches)
            extra = (
                f", {len(check.point_differences)} point differences"
                if check.point_differences
                else ""
            )
            print(f"   [{mark}] {check.label}: {check.teams} teams{extra}")
            for line in check.mismatches[: 20 if args.verbose else 3]:
                print(f"         {line}")
            if args.verbose:
                for line in check.point_differences:
                    print(f"         points: {line}")
    print(f"\n{bad} group(s) with mismatches")
    return 1 if bad else 0


def _europe_seasons(args: argparse.Namespace) -> tuple[list[str], str]:
    """Selected seasons and the running one (same window as the domestic data)."""
    pages = load_pages(paths.tff_pages_csv())
    current = max(p.season for p in pages if p.current)
    seasons = sorted({p.season for p in pages})
    if args.season:
        seasons = [s for s in seasons if s in args.season]
    if args.current_only:
        seasons = [current]
    return seasons, current


def cmd_europe_fetch(args: argparse.Namespace) -> int:
    started = time.monotonic()
    seasons, current = _europe_seasons(args)
    with PoliteClient(paths.wiki_cache_dir(), min_interval=args.interval) as client:
        for season in seasons:
            refresh = args.refresh_current and season == current
            for code in wiki.COMPETITIONS:
                articles = wiki.season_articles(client, code, season, refresh=refresh)
                if articles:
                    log.info(
                        "%s %s: %d articles, %s", code, season, len(articles), dict(client.stats)
                    )
        log.info(
            "europe-fetch done in %.0f min: %s",
            (time.monotonic() - started) / 60,
            dict(client.stats),
        )
    return 0


def _collect_europe(args: argparse.Namespace) -> list[SeasonData]:
    seasons, _ = _europe_seasons(args)
    tr_clubs = load_tr_clubs(paths.data_dir() / "sources" / "europe_tr_clubs.csv")
    out = []
    with PoliteClient(paths.wiki_cache_dir(), offline=True) as client:
        for season in seasons:
            articles = {
                code: wiki.season_articles(client, code, season) for code in wiki.COMPETITIONS
            }
            out.append(collect_season(season, articles, tr_clubs))
    return out


def cmd_europe_build(args: argparse.Namespace) -> int:
    data = _collect_europe(args)
    n_matches, n_coefs = write_europe(paths.europe_dir(), data)
    issues = sum(len(s.issues) for s in data)
    log.info(
        "%d matches, %d coefficients, %d issues (see `tlelo europe-check`)",
        n_matches,
        n_coefs,
        issues,
    )
    return 0


def cmd_europe_check(args: argparse.Namespace) -> int:
    bad = 0
    _, current = _europe_seasons(args)
    for season in _collect_europe(args):
        status: dict[str, int] = {}
        for m in season.matches:
            status[m.status] = status.get(m.status, 0) + 1
        print(f"\n## {season.season}: {len(season.matches)} matches {status}")
        problems = season.issues + check_season(season, finished=season.season != current)
        bad += len(problems)
        for line in problems:
            print(f"   {line}")
    print(f"\n{bad} problem(s)")
    return 1 if bad else 0


def cmd_elo(args: argparse.Namespace) -> int:
    from tlelo.elo.data import load_dataset
    from tlelo.elo.fit import run_model
    from tlelo.elo.output import write_ratings
    from tlelo.elo.params import MODEL_VERSION, V1

    data = load_dataset(paths.data_dir())
    res = run_model(data, V1)
    n_cur, n_hist = write_ratings(paths.data_dir() / "ratings", res, data)
    e = res.europe
    log.info(
        "model %s: %d clubs, %d history rows; Europe a=%.0f b=%.1f home=%.0f",
        MODEL_VERSION,
        n_cur,
        n_hist,
        e.a,
        e.b,
        e.home,
    )
    return 0


def cmd_site(args: argparse.Namespace) -> int:
    from tlelo.elo.data import load_dataset
    from tlelo.elo.fit import run_model
    from tlelo.elo.params import V1
    from tlelo.site.export import build, write, write_logos

    data = load_dataset(paths.data_dir())
    built = build(run_model(data, V1), data, paths.data_dir())
    out = paths.repo_root() / "web" / "src" / "data"
    n = write(out, built)
    logos = write_logos(paths.repo_root() / "web" / "public" / "logos", built)
    active = built["meta"]["activeTeams"]
    log.info("wrote %s: %d clubs (%d active), %d logos", out, n, active, logos)
    return 0


def cmd_logos(args: argparse.Namespace) -> int:
    from tlelo.elo.data import load_dataset
    from tlelo.http import PoliteClient
    from tlelo.site.export import visible_teams
    from tlelo.site.logos import fetch_logos
    from tlelo.site.names import load_masked

    data = load_dataset(paths.data_dir())
    masked = load_masked(paths.data_dir() / "sources" / "team_display_names.csv")
    teams = [t for t in visible_teams(data) if t not in masked]
    with PoliteClient(paths.raw_cache_dir(), min_interval=args.interval) as client:
        got = fetch_logos(client, teams)
        log.info("logos: %d of %d clubs (%s)", len(got), len(teams), dict(client.stats))
    return 0


def cmd_backtest(args: argparse.Namespace) -> int:
    from tlelo.elo.data import load_dataset
    from tlelo.elo.report import backtest_report

    started = time.monotonic()
    text = backtest_report(load_dataset(paths.data_dir()))
    out = paths.repo_root() / "docs" / "backtest.md"
    out.write_text(text, encoding="utf-8", newline="\n")
    log.info("wrote %s in %.0f s", out, time.monotonic() - started)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tlelo", description=__doc__.splitlines()[0])
    parser.add_argument("--log-file", help="also write logs to this file")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, func, help_text: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("-c", "--competition", nargs="+", choices=COMPETITIONS)
        p.add_argument("-s", "--season", nargs="+", metavar="2016-17")
        p.add_argument("--current-only", action="store_true", help="only the running season")
        p.set_defaults(func=func)
        return p

    for name, func, help_text in (
        ("fetch", cmd_fetch, "download season/group/week pages"),
        ("details", cmd_details, "download match detail pages"),
    ):
        p = add(name, func, help_text)
        p.add_argument("--interval", type=float, default=2.0, help="seconds between requests")
        if name == "fetch":
            p.add_argument("--refresh-current", action="store_true", help="re-download live pages")
    add("build", cmd_build, "write CSVs from the cache")
    add("validate", cmd_validate, "compare with TFF standings").add_argument(
        "-v", "--verbose", action="store_true"
    )

    p = sub.add_parser("europe-fetch", help="download Wikipedia articles of UEFA competitions")
    p.add_argument("-s", "--season", nargs="+", metavar="2016-17")
    p.add_argument("--current-only", action="store_true", help="only the running season")
    p.add_argument("--interval", type=float, default=2.0, help="seconds between requests")
    p.add_argument("--refresh-current", action="store_true", help="re-download live pages")
    p.set_defaults(func=cmd_europe_fetch)
    for name, func, help_text in (
        ("europe-build", cmd_europe_build, "write data/europe/*.csv from the cache"),
        ("europe-check", cmd_europe_check, "report gaps in the European data"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("-s", "--season", nargs="+", metavar="2016-17")
        p.add_argument("--current-only", action="store_true", help="only the running season")
        p.set_defaults(func=func)
    sub.add_parser("elo", help="compute the ratings into data/ratings/").set_defaults(func=cmd_elo)
    sub.add_parser("backtest", help="write docs/backtest.md").set_defaults(func=cmd_backtest)
    sub.add_parser("site", help="write web/src/data/*.json").set_defaults(func=cmd_site)
    p = sub.add_parser("logos", help="download the site's club logos from TFF into the cache")
    p.add_argument("--interval", type=float, default=2.0, help="seconds between requests")
    p.set_defaults(func=cmd_logos)

    args = parser.parse_args(argv)
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=handlers
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
