"""Readable club names and URL slugs.

TFF names carry the legal form and often a sponsor: "EKENLER BETON SİVASSPOR",
"GAZİANTEP FUTBOL KULÜBÜ A.Ş.". The site shows the name fans use. Generic rules drop the
legal form and set Turkish title case; ``data/sources/team_display_names.csv`` (kept by
hand) gives the name where a sponsor or an unusual form needs it. The official name stays
visible on the club's page.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

# Removed from the end of the name, repeatedly, longest first.
_TRAILING = (
    " SPORTİF YATIRIMLAR",
    " SPOR FAALİYETLERİ",
    " SPORTİF FAALİYETLER",
    " FUTBOL YATIRIMLARI",
    " SPOR YAT.",
    " FUTBOL SPOR KULÜBÜ",
    " FUTBOL SPOR",
    " FUTBOL",
    " A.Ş.",
    " A.Ş",
)
# Replaced at the end of the name.
_ENDINGS = (
    (" FK SPOR KULÜBÜ", " FK"),
    (" SPOR FUTBOL KULÜBÜ", " SPOR"),
    (" FUTBOL KULÜBÜ SK", " FK"),
    (" FUTBOL KULÜBÜ", " FK"),
    (" FUTBOL SK", " SPOR"),
    ("SPOR KULÜBÜ", "SPOR"),
    (" KULÜBÜ", ""),
)
_UPPER = {"FK", "SK", "MKE", "GMG", "KCT", "SMS", "BB", "G.O.G.", "D.Ç"}
_ASCII = str.maketrans("çğıöşüâîûÇĞİIÖŞÜ", "cgiosuaiuCGIIOSU")


def tr_lower(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()


def tr_title(s: str) -> str:
    """Turkish title case: 'İSTANBUL BAŞAKŞEHİR FK' -> 'İstanbul Başakşehir FK'."""
    words = []
    for w in s.split():
        if w in _UPPER:
            words.append(w)
            continue
        low = tr_lower(w)
        first = {"i": "İ", "ı": "I"}.get(low[0], low[0].upper())
        words.append(first + low[1:])
    return " ".join(words)


def clean_name(official: str) -> str:
    name = re.sub(r"\s+", " ", official.strip())
    changed = True
    while changed:
        changed = False
        for suffix in _TRAILING:
            if name.endswith(suffix) and len(name) > len(suffix) + 2:
                name, changed = name[: -len(suffix)], True
        for old, new in _ENDINGS:
            if name.endswith(old) and len(name) > len(old) + 2:
                name, changed = name[: -len(old)] + new, True
    return tr_title(name)


def load_overrides(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        return {int(r["team_id"]): r["display_name"] for r in csv.DictReader(fh)}


def display_name(team: int, official: str, overrides: dict[int, str]) -> str:
    return overrides.get(team) or clean_name(official)


def slugify(name: str) -> str:
    s = tr_lower(name).translate(_ASCII)
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def unique_slugs(names: dict[int, str]) -> dict[int, str]:
    """Slug per team; a clash (two clubs, one name) gets the TFF id appended."""
    base = {t: slugify(n) for t, n in names.items()}
    counts: dict[str, int] = {}
    for s in base.values():
        counts[s] = counts.get(s, 0) + 1
    return {t: (s if counts[s] == 1 else f"{s}-{t}") for t, s in base.items()}
