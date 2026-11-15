"""Club logos from the clubs' TFF pages (``uv run tlelo logos``).

Each club page (``pageId=28&kulupId=<id>``) shows the logo TFF holds for the club. Pages
and images are cached under ``data/raw/tff/`` (git-ignored); ``tlelo site`` copies the
images into the website. Clubs marked ``mask`` in ``team_display_names.csv`` are skipped.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import urlparse

from tlelo.http import PoliteClient

log = logging.getLogger(__name__)

CLUB_URL = "https://www.tff.org/Default.aspx?pageId=28&kulupId={}"
_LOGO = re.compile(r'<img id="[^"]*_dtKulupBilgisi_ad" src="([^"]+)"')


def logo_url(html: str) -> str | None:
    m = _LOGO.search(html)
    return m.group(1).replace("\\", "/") if m else None  # TFF writes a Windows path separator


def logo_path(cache_dir: Path, team: int) -> Path | None:
    found = sorted((cache_dir / "logos").glob(f"{team}.*"))
    return found[0] if found else None


def fetch_logos(client: PoliteClient, teams: list[int]) -> dict[int, Path]:
    out: dict[int, Path] = {}
    for team in teams:
        html = client.fetch(CLUB_URL.format(team), Path("clubs") / f"{team}.html.gz")
        url = logo_url(html)
        if url is None:
            log.warning("club %d: no logo on its TFF page", team)
            continue
        key = Path("logos") / f"{team}{Path(urlparse(url).path).suffix.lower() or '.png'}"
        client.fetch_bytes(url, key)
        out[team] = client.cache_dir / key
    return out
