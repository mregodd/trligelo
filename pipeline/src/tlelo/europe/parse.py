"""Parse Wikipedia's rendered (Parsoid) HTML: match boxes and UEFA coefficient tables.

Pure functions over HTML text, no network access.

Match boxes (``{{Football box}}``) carry an ISO date, the two teams (article link plus the
national association's flag link), the score, the goal minutes, a penalty shoot-out row
when there was one, the venue, and usually a uefa.com report link whose number is UEFA's
own match id. The score shown is the final one (after extra time); the 90-minute score
is rebuilt from the goal minutes when the match went to extra time.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html import unescape
from urllib.parse import unquote

TURKEY = "Turkish Football Federation"

_BOX = 'class="footballbox"'
_HEADING = re.compile(r"<h([2-4])\b[^>]*>(.*?)</h\1>", re.DOTALL)
_DATE = re.compile(r'class="bday dtstart[^"]*">(\d{4})-(\d{2})-(\d{2})<')
_TIME = re.compile(r'class="ftime">\s*(\d{1,2}[:.]\d{2})')
_HOME = re.compile(r'<th class="fhome"[^>]*>(.*?)</th>', re.DOTALL)
_AWAY = re.compile(r'<th class="faway"[^>]*>(.*?)</th>', re.DOTALL)
_SCORE = re.compile(r'<th class="fscore"[^>]*>(.*?)</th>', re.DOTALL)
_HGOALS = re.compile(r'<td class="fhgoal"[^>]*>(.*?)</td>', re.DOTALL)
_AGOALS = re.compile(r'<td class="fagoal"[^>]*>(.*?)</td>', re.DOTALL)
_SHOOTOUT = re.compile(
    r">Penalties</a>\s*</th>.*?<th[^>]*>\s*(\d+)\s*[–-]\s*(\d+)\s*</th>", re.DOTALL
)
_REPORT = re.compile(r'href="https?://(?:www\.)?uefa\.com/[^"]*?match[=/](\d+)')
_VENUE = re.compile(r'itemprop="name address"[^>]*>(.*?)</span>\s*</div>', re.DOTALL)
_FLAG_LINK = re.compile(
    r'<span class="flagicon"[^>]*>.*?<a href="https://en\.wikipedia\.org/wiki/([^"#?]+)',
    re.DOTALL,
)
_WIKI_LINK = re.compile(
    r'<a rel="mw:WikiLink" href="https://en\.wikipedia\.org/wiki/([^"#?]+)[^"]*"[^>]*>(.*?)</a>',
    re.DOTALL,
)
_FLAG_SPAN = re.compile(r'<span class="flagicon"[^>]*>.*?</a>\s*</span>\s*</span>', re.DOTALL)
_PAIR = re.compile(r"(\d+)\s*[–-]\s*(\d+)")
_MINUTE = re.compile(r"(\d{1,3})(?:\+\d{1,2})?'")
_TAG = re.compile(r"<[^>]+>")
_STYLE = re.compile(r"<style\b.*?</style>|<sup\b.*?</sup>", re.DOTALL)
_ROW = re.compile(r"<tr\b.*?</tr>", re.DOTALL)
_CELL = re.compile(r"<t[hd]\b[^>]*>(.*?)</t[hd]>", re.DOTALL)
_TABLE = re.compile(r"<table\b.*?</table>", re.DOTALL)
_COEFF = re.compile(r"^(\d{1,3}\.\d{3})$")


def text(html: str) -> str:
    s = _TAG.sub(" ", _STYLE.sub(" ", html))
    s = re.sub(r"\s+", " ", unescape(s)).strip()
    return re.sub(r"\s+([),])", r"\1", re.sub(r"\(\s+", "(", s))


def title_of(href_part: str) -> str:
    return unquote(href_part).replace("_", " ")


@dataclass(frozen=True, slots=True)
class Side:
    title: str | None  # linked article (may be a redirect); None when not linked
    name: str  # name as displayed
    association: str | None  # article of the national association (flag link)


@dataclass(frozen=True, slots=True)
class BoxMatch:
    section: str  # "Third qualifying round / Main Path matches"
    date: date | None
    time: str | None
    home: Side
    away: Side
    score: tuple[int, int] | None  # final score shown (after extra time if played)
    extra_time: bool
    regular: tuple[int, int] | None  # after 90 minutes; None if it cannot be rebuilt
    penalties: tuple[int, int] | None
    score_text: str  # raw cell text ("1–1 (a.e.t.)", "v", "Cancelled", "3–0 (awd.)")
    uefa_id: int | None
    venue: str | None


def parse_side(html: str) -> Side:
    flag = _FLAG_LINK.search(html)
    association = title_of(flag.group(1)) if flag else None
    rest = _FLAG_SPAN.sub(" ", html)
    link = _WIKI_LINK.search(rest)
    title = title_of(link.group(1)) if link else None
    return Side(title, text(rest), association)


def _goal_minutes(cell: str | None) -> list[int]:
    return [int(m) for m in _MINUTE.findall(text(cell))] if cell else []


def _pair(s: str) -> tuple[int, int] | None:
    m = _PAIR.search(s)
    return (int(m.group(1)), int(m.group(2))) if m else None


def parse_box(chunk: str, section: str = "") -> BoxMatch:
    d = _DATE.search(chunk)
    t = _TIME.search(chunk)
    home = _HOME.search(chunk)
    away = _AWAY.search(chunk)
    score_cell = _SCORE.search(chunk)
    score_text = text(score_cell.group(1)) if score_cell else ""
    score = _pair(score_text)
    extra_time = "a.e.t" in score_text

    regular = score
    if score and extra_time:
        hg = _HGOALS.search(chunk)
        ag = _AGOALS.search(chunk)
        h_min = _goal_minutes(hg.group(1) if hg else None)
        a_min = _goal_minutes(ag.group(1) if ag else None)
        if (len(h_min), len(a_min)) == score:  # every goal listed with its minute
            regular = (sum(m <= 90 for m in h_min), sum(m <= 90 for m in a_min))
        else:
            regular = None
    pens = _SHOOTOUT.search(chunk)
    report = _REPORT.search(chunk)
    venue = _VENUE.search(chunk)
    return BoxMatch(
        section=section,
        date=date(int(d[1]), int(d[2]), int(d[3])) if d else None,
        time=t.group(1).replace(".", ":") if t else None,
        home=parse_side(home.group(1)) if home else Side(None, "", None),
        away=parse_side(away.group(1)) if away else Side(None, "", None),
        score=score,
        extra_time=extra_time,
        regular=regular,
        penalties=(int(pens[1]), int(pens[2])) if pens else None,
        score_text=score_text,
        uefa_id=int(report.group(1)) if report else None,
        venue=text(venue.group(1)) if venue else None,
    )


def _sections(html: str) -> list[tuple[int, str]]:
    """(position, "h2 / h3 / h4" path) at every heading."""
    path: dict[int, str] = {}
    out = []
    for m in _HEADING.finditer(html):
        level = int(m.group(1))
        path[level] = text(m.group(2))
        for deeper in [k for k in path if k > level]:
            del path[deeper]
        out.append((m.start(), " / ".join(path[k] for k in sorted(path))))
    return out


def parse_boxes(html: str) -> list[BoxMatch]:
    sections = _sections(html)
    starts = [m.start() for m in re.finditer(re.escape(_BOX), html)]
    out = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else min(len(html), start + 40000)
        section = ""
        for pos, path in sections:
            if pos > start:
                break
            section = path
        out.append(parse_box(html[start:end], section))
    return out


@dataclass(frozen=True, slots=True)
class Coefficient:
    title: str  # club article, or the association's article for association rows
    name: str
    association: str | None  # None: an association ranking row (its flag has no link)
    value: float

    @property
    def is_club(self) -> bool:
        return self.association is not None


def parse_coefficients(html: str) -> list[Coefficient]:
    """Rows of every table with a "Coeff." column (older pages: "Coeff").

    Club rows come from draw / team tables, where the flag links to the club's national
    association. The season page's association ranking uses flags without a link, so its
    rows come back with ``association=None`` and the association article as ``title``.

    A row can hold several team/coefficient pairs (seeded and unseeded side by side), so
    cells are read in order and each value goes to the last club seen without one.
    """
    out = []
    for table in _TABLE.findall(html):
        if "Coeff" not in table:
            continue
        for row in _ROW.findall(table):
            pending: Side | None = None
            for cell in _CELL.findall(row):
                if 'class="flagicon"' in cell:
                    side = parse_side(cell)
                    pending = side if side.title else None
                    continue
                m = _COEFF.match(text(cell))
                if m and pending is not None:
                    out.append(
                        Coefficient(pending.title, pending.name, pending.association, float(m[1]))
                    )
                    pending = None
    return out
