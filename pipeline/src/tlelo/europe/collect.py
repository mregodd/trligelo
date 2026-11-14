"""Turkish clubs' UEFA matches and their opponents' club coefficients, per season.

Identifiers: foreign clubs are identified by their English Wikipedia article title, Turkish
clubs by TFF's ``kulupID`` (``data/sources/europe_tr_clubs.csv`` maps one to the other).
Article titles in match boxes can be redirects, and a repeated team is often not linked
at all, so names are resolved through an index of (association, displayed name) built
from every linked team of the season.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from tlelo.europe.parse import TURKEY, BoxMatch, Side, parse_boxes, parse_coefficients
from tlelo.europe.wiki import COMPETITIONS, Article

# Checked in order against the round heading (the first heading level of the section).
ROUNDS = (
    (r"preliminary", "PR"),
    (r"first qualifying", "Q1"),
    (r"second qualifying", "Q2"),
    (r"third qualifying", "Q3"),
    (r"knockout (?:round |phase )?play-off", "KPO"),
    (r"play-off", "PO"),
    (r"round of 32", "R32"),
    (r"round of 16", "R16"),
    (r"quarter-final", "QF"),
    (r"semi-final", "SF"),
    (r"\bfinal\b", "F"),
)
FORFEIT_WORDS = ("awd", "awarded", "w/o", "walkover", "forfeit")


def round_code(page_title: str, section: str) -> tuple[str | None, str | None]:
    """(round, group) for a box: group / league phase pages, else the round heading."""
    page = page_title.lower()
    group = re.search(r"\bGroup ([A-L])\b", section)
    if "group stage" in page:
        return "GS", group.group(1) if group else None
    if "league phase" in page:
        return "LP", None
    head = section.split(" / ")[0].lower()
    for pattern, code in ROUNDS:
        if re.search(pattern, head):
            return code, None
    return None, None


@dataclass(slots=True)
class EuropeMatch:
    match_id: int | None  # UEFA's match id (uefa.com report link)
    season: str
    competition: str  # UCL | UEL | UECL
    round: str | None  # PR Q1 Q2 Q3 PO GS LP KPO R32 R16 QF SF F
    group: str | None
    leg: int | None  # 1 / 2 for two-legged ties
    date: date | None
    time: str | None  # local kick-off time
    home_team: str | None  # Wikipedia article title
    home_name: str
    home_assoc: str | None
    away_team: str | None
    away_name: str
    away_assoc: str | None
    team_id: int | None  # TFF kulupID of the Turkish side
    tr_home: bool  # Turkish club is the home side
    opponent: str | None
    opponent_coefficient: float | None
    home_goals: int | None  # after 90 minutes
    away_goals: int | None
    et_home: int | None
    et_away: int | None
    pen_home: int | None
    pen_away: int | None
    status: str  # played | forfeit | not_played
    venue: str | None
    source: str  # Wikipedia article


@dataclass(slots=True)
class SeasonData:
    season: str
    matches: list[EuropeMatch] = field(default_factory=list)
    # club article -> (name, association, coefficient)
    coefficients: dict[str, tuple[str, str | None, float]] = field(default_factory=dict)
    # association article -> (country name, association coefficient)
    associations: dict[str, tuple[str, float]] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)


def load_tr_clubs(path: Path) -> dict[str, int]:
    """Wikipedia article title of a Turkish club -> TFF kulupID."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        return {r["wiki_title"]: int(r["team_id"]) for r in csv.DictReader(fh)}


def _norm(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().casefold()


class NameIndex:
    """(association, displayed name) -> article title, ambiguous names dropped."""

    def __init__(self) -> None:
        self._titles: dict[tuple[str | None, str], set[str]] = defaultdict(set)

    def add(self, title: str | None, name: str, association: str | None) -> None:
        if title and name:
            self._titles[(association, _norm(name))].add(title)
            self._titles[(association, _norm(title))].add(title)

    def resolve(self, side: Side) -> str | None:
        if side.title:
            return side.title
        found = self._titles.get((side.association, _norm(side.name)), set())
        return next(iter(found)) if len(found) == 1 else None


def collect_season(
    season: str, articles: dict[str, list[Article]], tr_clubs: dict[str, int]
) -> SeasonData:
    """``articles``: competition code -> the season's Wikipedia articles."""
    data = SeasonData(season)
    index = NameIndex()
    values: dict[str, Counter[float]] = defaultdict(Counter)
    assoc_values: dict[str, Counter[float]] = defaultdict(Counter)
    assoc_names: dict[str, str] = {}
    parsed: list[tuple[str, str, BoxMatch]] = []

    for code in COMPETITIONS:
        for art in articles.get(code, []):
            for c in parse_coefficients(art.html):
                if not c.is_club:
                    assoc_values[c.title][c.value] += 1
                    assoc_names.setdefault(c.title, c.name)
                    continue
                values[c.title][c.value] += 1
                index.add(c.title, c.name, c.association)
                data.coefficients.setdefault(c.title, (c.name, c.association, c.value))
            for box in parse_boxes(art.html):
                index.add(box.home.title, box.home.name, box.home.association)
                index.add(box.away.title, box.away.name, box.away.association)
                if TURKEY in (box.home.association, box.away.association):
                    parsed.append((code, art.title, box))

    for title, counts in values.items():
        if len(counts) > 1:
            data.issues.append(f"club coefficient differs between tables: {title} {dict(counts)}")
            name, assoc, _ = data.coefficients[title]
            data.coefficients[title] = (name, assoc, counts.most_common(1)[0][0])
    for title, counts in assoc_values.items():
        # The three season pages repeat one ranking; a lone different value is a typo.
        data.associations[title] = (assoc_names[title], counts.most_common(1)[0][0])

    by_name = {(a, _norm(n)): t for t, (n, a, _) in data.coefficients.items()}
    seen: set[tuple] = set()
    for code, page, box in parsed:
        # Pages from 2022-23 on have no uefa.com report links, so the UEFA id is optional:
        # a match is the same if the date and both (resolved) clubs are.
        key = tuple(
            [box.date] + [index.resolve(side) or _norm(side.name) for side in (box.home, box.away)]
        )
        if key in seen:
            continue  # same match on another page (e.g. the final)
        seen.add(key)
        data.matches.append(_record(data, code, page, box, index, by_name, tr_clubs))

    _assign_legs(data.matches)
    data.matches.sort(key=lambda m: (m.date or date.max, m.time or "", m.home_name))
    return data


def _record(data, code, page, box, index, by_name, tr_clubs) -> EuropeMatch:
    home_t, away_t = index.resolve(box.home), index.resolve(box.away)
    tr_home = box.home.association == TURKEY
    tr_side, opp_side = (box.home, box.away) if tr_home else (box.away, box.home)
    tr_title, opp_title = (home_t, away_t) if tr_home else (away_t, home_t)
    if box.home.association == TURKEY and box.away.association == TURKEY:
        data.issues.append(f"two Turkish clubs: {box.home.name} - {box.away.name}")

    team_id = tr_clubs.get(tr_title or "")
    if team_id is None:
        data.issues.append(f"Turkish club not mapped: {tr_title or tr_side.name!r}")

    coef = data.coefficients.get(opp_title or "")
    if coef is None:  # redirect or differently linked: try the displayed name
        alt = by_name.get((opp_side.association, _norm(opp_side.name)))
        if alt:
            opp_title, coef = alt, data.coefficients[alt]
    if coef is None:
        data.issues.append(
            f"no coefficient: {opp_title or opp_side.name!r} ({opp_side.association})"
        )

    rnd, group = round_code(page, box.section)
    if rnd is None:
        data.issues.append(f"unknown round: {page} / {box.section}")

    status = "played"
    if box.score is None:
        status = "not_played"
    elif any(w in box.score_text.lower() for w in FORFEIT_WORDS):
        status = "forfeit"
    if box.score and box.regular is None:
        data.issues.append(f"90-minute score unknown: {box.date} {box.home.name}-{box.away.name}")
    if box.date is None:
        data.issues.append(f"no date: {box.home.name}-{box.away.name} ({page})")

    reg = box.regular
    et = box.score if box.extra_time else None
    return EuropeMatch(
        match_id=box.uefa_id,
        season=data.season,
        competition=code,
        round=rnd,
        group=group,
        leg=None,
        date=box.date,
        time=box.time,
        home_team=home_t,
        home_name=box.home.name,
        home_assoc=box.home.association,
        away_team=away_t,
        away_name=box.away.name,
        away_assoc=box.away.association,
        team_id=team_id,
        tr_home=tr_home,
        opponent=opp_title,
        opponent_coefficient=coef[2] if coef else None,
        home_goals=reg[0] if reg else None,
        away_goals=reg[1] if reg else None,
        et_home=et[0] if et else None,
        et_away=et[1] if et else None,
        pen_home=box.penalties[0] if box.penalties else None,
        pen_away=box.penalties[1] if box.penalties else None,
        status=status,
        venue=box.venue,
        source=page,
    )


TWO_LEGGED = {"PR", "Q1", "Q2", "Q3", "PO", "KPO", "R32", "R16", "QF", "SF"}


def _assign_legs(matches: list[EuropeMatch]) -> None:
    """Two matches of the same tie (round, Turkish club, opponent) are legs 1 and 2."""
    ties: dict[tuple, list[EuropeMatch]] = defaultdict(list)
    for m in matches:
        if m.round in TWO_LEGGED:
            ties[(m.competition, m.round, m.team_id, m.opponent)].append(m)
    for legs in ties.values():
        if len(legs) == 2:
            legs.sort(key=lambda m: m.date or date.max)
            legs[0].leg, legs[1].leg = 1, 2
