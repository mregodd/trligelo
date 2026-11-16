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

import numpy as np
from PIL import Image
from scipy import ndimage

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


_DISK = np.hypot(*np.mgrid[-2:3, -2:3]) <= 2  # closes breaks of up to ~4 px in an outline


def transparent_png(src: Path, dst: Path) -> None:
    """Save a logo as PNG with its plain light background removed.

    TFF serves most logos as JPEG on white, which shows as a white square on tinted rows and
    dark grounds; a few come on black or on a white-to-grey gradient. Logos that already come
    cut out (a mostly transparent edge) are kept as they are. Otherwise the plain ground,
    told by the colour of the image edge, becomes transparent where it is connected to the
    edge, except inside the crest's silhouette: its other parts with small breaks in the
    outline closed and the inside filled, so white within the outline stays even where the
    outline is broken. A 2px fringe around the removed area fades by how close it is to the
    ground, so anti-aliased edges leave no halo.
    """
    rgba = np.array(Image.open(src).convert("RGBA"))
    if (_edge(rgba[..., 3]) < 128).mean() > 0.5:
        Image.fromarray(rgba).save(dst, optimize=True)
        return
    rgb = rgba[..., :3].astype(float)
    low, high = rgb.min(axis=2), rgb.max(axis=2)
    neutral = high - low <= 24
    edge_neutral = _edge(neutral)
    if (edge_neutral & (_edge(high) <= 23)).mean() > 0.5:  # on black
        plain, fade = neutral & (high <= 23), np.clip(high / 75, 0, 1)
    else:
        # On a gradient the ground runs from white down to light grey; plain white otherwise.
        edge_light = _edge(low)[edge_neutral & (_edge(low) >= 180)]
        graded = len(edge_light) > edge_neutral.size / 2 and np.percentile(edge_light, 25) < 225
        plain = neutral & (low >= (180 if graded else 232))
        fade = np.clip((255 - low) / (255 - 180), 0, 1)
    pad = len(_DISK)  # room for the closing at the image edge
    inked = ndimage.binary_closing(np.pad(~plain, pad), _DISK)
    shape = ndimage.binary_fill_holes(inked)[pad:-pad, pad:-pad]
    labels, _ = ndimage.label(plain & ~shape)
    edge = np.unique(_edge(labels))
    background = np.isin(labels, edge[edge > 0])
    fringe = ndimage.binary_dilation(background, iterations=2) & ~background
    alpha = rgba[..., 3].astype(float)
    alpha[background] = 0
    alpha[fringe] *= fade[fringe]
    rgba[..., 3] = alpha.round().astype(np.uint8)
    Image.fromarray(rgba).save(dst, optimize=True)


def _edge(a: np.ndarray) -> np.ndarray:
    """The outermost pixels of an image (or of one of its channels), in one run."""
    return np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
