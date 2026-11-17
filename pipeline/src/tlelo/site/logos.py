"""Club logos from the clubs' TFF pages (``uv run tlelo logos``).

Each club page (``pageId=28&kulupId=<id>``) shows the logo TFF holds for the club. Pages
and images are cached under ``data/raw/tff/`` (git-ignored); ``tlelo site`` copies the
images into the website. Clubs marked ``mask`` in ``team_display_names.csv`` are skipped.

The images come from fys.tff.org, which does not answer GitHub's servers: run this locally
and push ``data/raw/tff/logos`` (its own git repo) to the private logo repo the CI reads.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from urllib.parse import urlparse

import httpx
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
    """Logos are cosmetic, so a failure never stops the data update: a club whose page or
    image is refused is skipped, and when TFF stops answering the rest waits for the next
    run (the cache keeps what was downloaded)."""
    out: dict[int, Path] = {}
    for team in teams:
        try:
            html = client.fetch(CLUB_URL.format(team), Path("clubs") / f"{team}.html.gz")
            url = logo_url(html)
            if url is None:
                log.warning("club %d: no logo on its TFF page", team)
                continue
            key = Path("logos") / f"{team}{Path(urlparse(url).path).suffix.lower() or '.png'}"
            client.fetch_bytes(url, key)
        except httpx.HTTPStatusError as exc:
            log.warning("club %d: logo skipped (%s)", team, exc)
            continue
        except RuntimeError as exc:  # retries used up
            log.warning("club %d: %s; remaining logos left for the next run", team, exc)
            break
        out[team] = client.cache_dir / key
    return out


_DISK = np.hypot(*np.mgrid[-2:3, -2:3]) <= 2  # closes breaks of up to ~4 px in an outline


def transparent_png(src: Path, dst: Path) -> None:
    """Save a logo as a square PNG, its background removed and the crest filling the square."""
    Image.fromarray(fill_square(cut_out(src))).save(dst, optimize=True)


def fill_square(rgba: np.ndarray) -> np.ndarray:
    """Crop to the crest and centre it on a square: images come with margins of every size
    (and some are not square), which would leave some crests small in their slot."""
    ys, xs = np.nonzero(rgba[..., 3] > 16)
    if len(ys) == 0:
        return rgba
    crop = rgba[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1]
    h, w = crop.shape[:2]
    side = max(h, w)
    out = np.zeros((side, side, 4), np.uint8)
    top, left = (side - h) // 2, (side - w) // 2
    out[top : top + h, left : left + w] = crop
    return out


def cut_out(src: Path) -> np.ndarray:
    """A logo as RGBA with its plain background made transparent.

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
        return rgba
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
    return rgba


def _edge(a: np.ndarray) -> np.ndarray:
    """The outermost pixels of an image (or of one of its channels), in one run."""
    return np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
