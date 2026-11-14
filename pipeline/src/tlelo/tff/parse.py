"""Parsers for tff.org pages.

Pure functions: page HTML in, records out. No network access, so every parser can be
tested against saved snippets of real pages. The site's markup is old ASP.NET with nested
layout tables, so the parsers work on small, well-anchored regular expressions instead of
a DOM walk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html import unescape

Score = tuple[int, int]

TR_MONTHS = {
    "ocak": 1,
    "şubat": 2,
    "mart": 3,
    "nisan": 4,
    "mayıs": 5,
    "haziran": 6,
    "temmuz": 7,
    "ağustos": 8,
    "eylül": 9,
    "ekim": 10,
    "kasım": 11,
    "aralık": 12,
}


@dataclass(frozen=True, slots=True)
class FixtureRow:
    """A row of a season's full fixture list (no dates on this view)."""

    match_id: int
    week: int
    table_group: str | None  # normalized group key from the table title
    home_id: int
    home_name: str
    away_id: int
    away_name: str
    score: Score | None  # None = not played


@dataclass(frozen=True, slots=True)
class DatedRow:
    """A row of a week view: gives the kick-off date and time of a match."""

    match_id: int
    date: date
    time: str | None
    score: Score | None
    home_id: int
    home_name: str
    away_id: int
    away_name: str


@dataclass(frozen=True, slots=True)
class CupRow:
    """A knock-out style row (cup rounds, league play-offs)."""

    match_id: int
    round: str
    date: date
    time: str | None
    home_id: int
    home_name: str
    away_id: int
    away_name: str
    score: Score | None  # regular-time score as printed
    extra_time: Score | None  # score after extra time, "(Uzt. 2-1)"
    penalties: Score | None  # shoot-out, "(Pen. 4-3)"


@dataclass(frozen=True, slots=True)
class StandingRow:
    team_id: int
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    points: int


@dataclass(frozen=True, slots=True)
class MatchDetail:
    match_id: int
    venue_id: int | None
    venue: str | None
    has_officials: bool  # referees listed; forfeits (hükmen) have none
    home_id: int | None = None
    home_name: str | None = None
    away_id: int | None = None
    away_name: str | None = None
    score: Score | None = None
    date: date | None = None
    time: str | None = None


# --- helpers -----------------------------------------------------------------------------


def clean_text(fragment: str) -> str:
    """Strip tags, decode entities and collapse whitespace."""
    text = unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"\s+", " ", text).strip()


_GROUP_WORD = re.compile(r"\bgru(?:p|bu)\b", re.IGNORECASE)


def parse_score(text: str) -> Score | None:
    m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", unescape(text))
    return (int(m[1]), int(m[2])) if m else None


def normalize_group(label: str) -> str:
    """Normalize a group label so link texts and table titles compare equal.

    "01" / "01 Grup" / "1. Grup Grup" -> "1";  "Kırmızı" / "KIRMIZI GRUP" -> "kirmizi";
    "A Grubu" -> "a".
    """
    s = clean_text(label).casefold().replace("̇", "").replace("ı", "i")
    s = re.sub(_GROUP_WORD, " ", s)
    s = re.sub(r"[.\s]+", " ", s).strip()
    return str(int(s)) if s.isdigit() else s


def _split_rows(html: str) -> list[str]:
    return re.split(r"<tr\b", html, flags=re.IGNORECASE)


# --- groups ------------------------------------------------------------------------------

_GROUP_LINK = re.compile(r'grupID=(\d+)#grp"?[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)


def parse_groups(html: str) -> dict[int, str]:
    """Group id -> label, e.g. {1354: "Beyaz", 1355: "Kırmızı"}. Empty if not grouped."""
    groups: dict[int, str] = {}
    for gid, label in _GROUP_LINK.findall(html):
        text = clean_text(label)
        if text:
            groups.setdefault(int(gid), text)
    return groups


# --- full fixture list -------------------------------------------------------------------

_FIXTURE_TOKENS = re.compile(
    r'<span style="display:inline-block;font-size:11pt;font-weight:bold;[^"]*">'
    r"(?P<title>.*?)</span>"
    r'|class="belirginYazi"[^>]*>\s*(?P<week>\d+)\.\s*Hafta'
    r'|kulupId=(?P<hid>\d+)">(?P<hname>[^<]*)</a></td>\s*<td[^>]*>'
    r'<a href="/Default\.aspx\?pageID=29&(?:amp;)?macId=(?P<mid>\d+)">'
    r"(?P<score>[^<]*)</a></td>\s*"
    r'<td[^>]*><a href="/Default\.aspx\?pageID=28&(?:amp;)?kulupId=(?P<aid>\d+)">'
    r"(?P<aname>[^<]*)</a>",
    re.IGNORECASE | re.DOTALL,
)


def _title_group(title_html: str) -> str | None:
    lines = [clean_text(part) for part in re.split(r"<br\s*/?>", title_html, flags=re.I)]
    for line in lines[1:]:
        if _GROUP_WORD.search(line):
            return normalize_group(line)
    # Some seasons put the group on the first line: "Spor Toto 2.Lig Beyaz Grup".
    m = re.search(r"(\S+)\s+gru(?:p|bu)\s*$", lines[0], re.IGNORECASE) if lines else None
    return normalize_group(m[1]) if m else None


def parse_fixture(html: str) -> list[FixtureRow]:
    """All rows of every fixture-list table on the page, deduplicated by match id."""
    rows: dict[int, FixtureRow] = {}
    group: str | None = None
    week = 0
    for m in _FIXTURE_TOKENS.finditer(html):
        if m["title"] is not None:
            group, week = _title_group(m["title"]), 0
        elif m["week"] is not None:
            week = int(m["week"])
        else:
            mid = int(m["mid"])
            rows.setdefault(
                mid,
                FixtureRow(
                    match_id=mid,
                    week=week,
                    table_group=group,
                    home_id=int(m["hid"]),
                    home_name=clean_text(m["hname"]),
                    away_id=int(m["aid"]),
                    away_name=clean_text(m["aname"]),
                    score=parse_score(m["score"]),
                ),
            )
    return list(rows.values())


def rows_for_group(rows: list[FixtureRow], label: str | None) -> list[FixtureRow]:
    """Keep the rows of one group when a page lists several groups' tables.

    Some seasons show the same (first) group's fixture list on every group page, so a
    table titled with another group is never borrowed. An empty result means the
    group's matches have to be read from its week views instead.
    """
    if label is None:
        return rows
    key = normalize_group(label)
    matching = [r for r in rows if r.table_group == key]
    if matching:
        return matching
    if rows and all(r.table_group is None for r in rows):
        return rows  # single table whose title does not name a group
    return []


# --- week view (dates) -------------------------------------------------------------------

_SHORT_DATE = re.compile(r">\s*(\d{2})\.(\d{2})\.(\d{4})\s*<")
_TIME = re.compile(r">\s*(\d{1,2}:\d{2})\s*<")
_MATCH_LINK = re.compile(r"macId=(\d+)[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)


_TEAM_ANCHOR = re.compile(r'kulupID=(\d+)"[^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)


def parse_week_dates(html: str) -> dict[int, DatedRow]:
    """Match id -> date, time, score and teams for every dated match row on a week view.

    Two layouts exist: "haftaninMaclari" (single-table leagues, names inside <span>) and
    "kupaMaclari" (grouped leagues and cup groups, names directly in the link).
    """
    out: dict[int, DatedRow] = {}
    for chunk in _split_rows(html):
        link = _MATCH_LINK.search(chunk)
        teams = _TEAM_ANCHOR.findall(chunk)
        if not link or len(teams) < 2:
            continue
        head = chunk[: link.start()]
        d = _SHORT_DATE.search(head)
        if not d:
            continue
        t = _TIME.search(head, d.end())
        mid = int(link[1])
        out[mid] = DatedRow(
            match_id=mid,
            date=date(int(d[3]), int(d[2]), int(d[1])),
            time=t[1] if t else None,
            score=parse_score(clean_text(link[2])),
            home_id=int(teams[0][0]),
            home_name=clean_text(teams[0][1]),
            away_id=int(teams[1][0]),
            away_name=clean_text(teams[1][1]),
        )
    return out


_WEEK_LINK = re.compile(r"[?&](?:amp;)?hafta=(\d+)", re.IGNORECASE)


def parse_week_links(html: str) -> list[int]:
    """Week numbers offered by the page's week navigation."""
    return sorted({int(w) for w in _WEEK_LINK.findall(html)})


# --- cup rounds and play-offs ------------------------------------------------------------

_CUP_HEADER = re.compile(
    r'class="alanTurkiyeKupasi"[^>]*>\s*<b>\s*<span[^>]*>([^<]*\S[^<]*)</span>', re.IGNORECASE
)
_LONG_DATE = re.compile(
    r"<span[^>]*>\s*(\d{1,2})\s+([^\s<\d]+)\s+(\d{4})(?:\s+(\d{1,2}:\d{2}))?\s*</span>"
)
_TEAM_LINK = re.compile(r'kulupID=(\d+)"[^>]*>([^<]+)</a>', re.IGNORECASE)
_EXTRA_TIME = re.compile(r"Uzt\.?\s*(\d+)\s*-\s*(\d+)", re.IGNORECASE)
_PENALTIES = re.compile(r"Pen\.?\s*(\d+)\s*-\s*(\d+)", re.IGNORECASE)


def _turkish_lower(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()


def parse_cup_rows(html: str) -> list[CupRow]:
    """Rows under "… Maçları" section headers (cup rounds, league play-offs)."""
    rows: dict[int, CupRow] = {}
    current_round = ""
    for chunk in _split_rows(html):
        header = _CUP_HEADER.search(chunk)
        if header:
            current_round = clean_text(header[1])
            continue
        link = _MATCH_LINK.search(chunk)
        d = _LONG_DATE.search(chunk)
        if not link or not d:
            continue
        month = TR_MONTHS.get(_turkish_lower(d[2]))
        teams = _TEAM_LINK.findall(chunk)
        if month is None or len(teams) < 2:
            continue
        tail = clean_text(chunk[link.end() :])
        et, pens = _EXTRA_TIME.search(tail), _PENALTIES.search(tail)
        mid = int(link[1])
        rows.setdefault(
            mid,
            CupRow(
                match_id=mid,
                round=current_round,
                date=date(int(d[3]), month, int(d[1])),
                time=d[4],
                home_id=int(teams[0][0]),
                home_name=clean_text(teams[0][1]),
                away_id=int(teams[1][0]),
                away_name=clean_text(teams[1][1]),
                score=parse_score(clean_text(link[2])),
                extra_time=(int(et[1]), int(et[2])) if et else None,
                penalties=(int(pens[1]), int(pens[2])) if pens else None,
            ),
        )
    return list(rows.values())


# --- standings ---------------------------------------------------------------------------

_STANDING_TEAM = re.compile(r'grvACetvel_ctl\d+_lnkTakim"[^>]*kulupID=(\d+)"', re.IGNORECASE)
_NUMBER_SPAN = re.compile(r"<span[^>]*>\s*(-?\d+)\s*</span>")


def parse_standings(html: str) -> list[StandingRow]:
    """The overall standings table (O, G, B, M, A, Y, AV, P)."""
    out: list[StandingRow] = []
    for chunk in _split_rows(html):
        team = _STANDING_TEAM.search(chunk)
        if not team:
            continue
        nums = [int(n) for n in _NUMBER_SPAN.findall(chunk[team.end() :])]
        if len(nums) < 8:
            continue
        played, won, drawn, lost, gf, ga, _gd, points = nums[:8]
        out.append(StandingRow(int(team[1]), played, won, drawn, lost, gf, ga, points))
    return out


# --- match detail ------------------------------------------------------------------------

_VENUE = re.compile(r'lnkStad"[^>]*stadId=(\d+)"[^>]*>([^<]*)</a>', re.IGNORECASE)
_OFFICIALS = re.compile(r'<div class="dtMacBilgisiHakemler">(.*?)</div>', re.IGNORECASE | re.DOTALL)


_DETAIL_TEAM = re.compile(
    r'dtMacBilgisi_lnkTakim([12])"[^>]*kulupId=(\d+)"[^>]*>([^<]*)</a>', re.IGNORECASE
)
# Home goals: "lblTakim1Skor"; away goals: "Label12" (older pages: "lblTakim2Skor").
_DETAIL_GOALS = re.compile(
    r'dtMacBilgisi_(lblTakim1Skor|lblTakim2Skor|Label12)"[^>]*>\s*(\d+)\s*<', re.IGNORECASE
)
_DETAIL_DATE = re.compile(
    r'dtMacBilgisi_lblTarih"[^>]*>\s*(\d{2})\.(\d{2})\.(\d{4})(?:\s*-\s*(\d{1,2}:\d{2}))?',
    re.IGNORECASE,
)


def parse_match_detail(match_id: int, html: str) -> MatchDetail:
    venue = _VENUE.search(html)
    officials = _OFFICIALS.search(html)
    has_officials = bool(officials and clean_text(officials[1])) or "(Hakem)" in html
    teams = {side: (int(tid), clean_text(name)) for side, tid, name in _DETAIL_TEAM.findall(html)}
    goals = {
        "1" if el.lower() == "lbltakim1skor" else "2": int(g)
        for el, g in _DETAIL_GOALS.findall(html)
    }
    d = _DETAIL_DATE.search(html)
    home, away = teams.get("1"), teams.get("2")
    return MatchDetail(
        match_id=match_id,
        venue_id=int(venue[1]) if venue else None,
        venue=clean_text(venue[2]) if venue else None,
        has_officials=has_officials,
        home_id=home[0] if home else None,
        home_name=home[1] if home else None,
        away_id=away[0] if away else None,
        away_name=away[1] if away else None,
        score=(goals["1"], goals["2"]) if len(goals) == 2 else None,
        date=date(int(d[3]), int(d[2]), int(d[1])) if d else None,
        time=d[4] if d else None,
    )
