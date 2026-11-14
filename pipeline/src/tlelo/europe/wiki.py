"""Find and download the Wikipedia articles of one UEFA competition-season.

Only article pages (``/wiki/<title>``) are read: Wikipedia's robots.txt allows them for
every client, while ``/w/`` and ``/api/`` are disallowed. Starting from the season page
("2018–19 UEFA Europa League"), every linked sub-article of the same season and
competition is followed (qualifying, group / league phase, knockout phase, and the
qualifying "matches" sub-pages some seasons use), at most ``MAX_DEPTH`` links deep.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from urllib.parse import quote, unquote

from tlelo.http import MissingPage, PoliteClient

log = logging.getLogger(__name__)

WIKI = "https://en.wikipedia.org/wiki/"
MAX_DEPTH = 2
FIRST_UECL = "2021-22"
UECL_RENAMED = "2024-25"  # "UEFA Europa Conference League" -> "UEFA Conference League"
COMPETITIONS = ("UCL", "UEL", "UECL")

_LINK = re.compile(r'href="https://en\.wikipedia\.org/wiki/([^"#?]+)')
_UNSAFE = re.compile(r'[<>:"/\\|?*%]')
_TITLE = re.compile(r"<title>(.*?) - Wikipedia</title>")


@dataclass(frozen=True, slots=True)
class Article:
    title: str
    html: str


def wiki_season(season: str) -> str:
    """``2018-19`` -> ``2018–19`` (Wikipedia titles use an en dash)."""
    return season.replace("-", "–")


def competition_name(code: str, season: str) -> str | None:
    if code == "UCL":
        return "UEFA Champions League"
    if code == "UEL":
        return "UEFA Europa League"
    if code == "UECL":
        if season < FIRST_UECL:
            return None
        return (
            "UEFA Conference League" if season >= UECL_RENAMED else "UEFA Europa Conference League"
        )
    raise ValueError(code)


def season_title(code: str, season: str) -> str | None:
    name = competition_name(code, season)
    return f"{wiki_season(season)} {name}" if name else None


def article_url(title: str) -> str:
    return WIKI + quote(title.replace(" ", "_"), safe="()_,'!-.~–")


def cache_key(title: str) -> Path:
    """File name for a title; characters Windows does not allow are percent-encoded."""
    name = _UNSAFE.sub(lambda m: f"%{ord(m.group()):02X}", title.replace(" ", "_"))
    return Path(f"{name}.html.gz")


def page_title(html: str) -> str | None:
    """The article's real title (a redirect is served under the target's title)."""
    m = _TITLE.search(html[:20000])
    return unescape(m.group(1)) if m else None


def linked_titles(html: str) -> list[str]:
    """Article titles linked from a page, in order, without duplicates."""
    seen: dict[str, None] = {}
    for raw in _LINK.findall(html):
        seen.setdefault(unquote(raw).replace("_", " "), None)
    return list(seen)


def sub_articles(html: str, prefix: str) -> list[str]:
    """Linked articles that belong to the same competition-season (``prefix ...``)."""
    return [t for t in linked_titles(html) if t.startswith(prefix + " ") and ":" not in t]


def season_articles(
    client: PoliteClient, code: str, season: str, *, refresh: bool = False
) -> list[Article]:
    """The season page and its sub-articles, breadth first.

    Redirects (several titles for one article) are kept once, under the real title.
    Missing pages are skipped with a warning.
    """
    root = season_title(code, season)
    if root is None:
        return []
    out: list[Article] = []
    seen = {root}
    real_titles: set[str] = set()
    frontier = [root]
    for depth in range(MAX_DEPTH + 1):
        nxt = []
        for title in frontier:
            try:
                html = client.fetch(article_url(title), cache_key(title), refresh=refresh)
            except MissingPage:
                log.warning("not cached: %s", title)
                continue
            except Exception as exc:  # 404 for a red link, etc.
                log.warning("skipping %s: %s", title, exc)
                continue
            real = page_title(html) or title
            if real in real_titles:
                continue
            real_titles.add(real)
            out.append(Article(real, html))
            if depth < MAX_DEPTH:
                for sub in sub_articles(html, root):
                    if sub not in seen:
                        seen.add(sub)
                        nxt.append(sub)
        frontier = nxt
    return out
