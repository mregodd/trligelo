"""Command line entry point: ``uv run tlelo <command>``.

Commands:
    fetch     download season, group and week pages into the cache
    details   download match detail pages (forfeit checks, play-off / final venues)
    build     write data/matches/*.csv and the team tables from the cache
    validate  compare parsed matches with TFF's standings tables
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from tlelo import paths
from tlelo.build import write_matches, write_teams
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
            try:
                out += [
                    d
                    for d in collect_supercup(client, _supercup_extra())
                    if not args.season or d.comp.season in args.season
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
    teams = write_teams(paths.data_dir(), data)
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
