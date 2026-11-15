"""A polite, caching HTTP client (tff.org pages and Wikipedia articles).

Every page is downloaded at most once and stored gzip-compressed (UTF-8) under the raw
cache directory. Requests are spaced by ``min_interval`` seconds and retried with backoff
on server errors, so a full backfill never puts noticeable load on the site.
"""

from __future__ import annotations

import gzip
import logging
import os
import time
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlencode

import httpx

log = logging.getLogger(__name__)

BASE_URL = "https://www.tff.org/Default.aspx"
# Generic, non-identifying client name. Override with TLELO_USER_AGENT if the project
# owner decides to publish a contact URL here.
USER_AGENT = os.environ.get(
    "TLELO_USER_AGENT", "Mozilla/5.0 (compatible; elo-research-client/0.1; non-commercial)"
)
RETRY_DELAYS = (10, 30, 60, 120)

Params = Mapping[str, int | str]


class MissingPage(LookupError):
    """Raised in offline mode when a page is not in the cache."""


def page_url(params: Params) -> str:
    return f"{BASE_URL}?{urlencode(dict(params))}"


def cache_key(params: Params) -> Path:
    """Map query parameters to a stable relative cache path.

    ``{"pageID": 1416, "grupID": 1356, "hafta": 5}`` -> ``p1416/grupID-1356_hafta-5.html.gz``.
    """
    page = params["pageID"]
    rest = sorted((k, v) for k, v in params.items() if k != "pageID")
    name = "_".join(f"{k}-{v}" for k, v in rest) or "index"
    return Path(f"p{page}") / f"{name}.html.gz"


class PoliteClient:
    def __init__(
        self,
        cache_dir: Path,
        *,
        min_interval: float = 2.0,
        timeout: float = 60.0,
        offline: bool = False,
    ) -> None:
        self.cache_dir = cache_dir
        self.min_interval = min_interval
        self.offline = offline
        self.stats: Counter[str] = Counter()
        self._last_request = 0.0
        self._http = httpx.Client(
            headers={"User-Agent": USER_AGENT, "Accept-Language": "tr-TR,tr;q=0.9"},
            timeout=timeout,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> PoliteClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def is_cached(self, params: Params) -> bool:
        return self.has(cache_key(params))

    def has(self, key: Path) -> bool:
        return (self.cache_dir / key).exists()

    def get(self, params: Params, *, refresh: bool = False) -> str:
        """Return a tff.org page's HTML as text, from cache when possible."""
        return self.fetch(page_url(params), cache_key(params), refresh=refresh)

    def fetch(self, url: str, key: Path, *, refresh: bool = False) -> str:
        """Return ``url`` as text, cached under ``cache_dir / key``."""
        path = self.cache_dir / key
        if path.exists() and not refresh:
            self.stats["cache"] += 1
            return gzip.decompress(path.read_bytes()).decode("utf-8")
        if self.offline:
            raise MissingPage(url)

        response = self._download(url, lambda body: b"</html>" in body[-2000:].lower())
        charset = response.charset_encoding or "windows-1254"
        text = response.content.decode(charset, errors="replace")
        self._store(path, gzip.compress(text.encode("utf-8")))
        return text

    def fetch_bytes(self, url: str, key: Path) -> bytes:
        """Return ``url`` (an image) as bytes, cached unchanged under ``cache_dir / key``."""
        path = self.cache_dir / key
        if path.exists():
            self.stats["cache"] += 1
            return path.read_bytes()
        if self.offline:
            raise MissingPage(url)
        body = self._download(url, bool).content
        self._store(path, body)
        return body

    def _store(self, path: Path, body: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(body)
        tmp.replace(path)
        self.stats["downloaded"] += 1

    def _download(self, url: str, complete) -> httpx.Response:
        """GET with retries; ``complete(body)`` tells a whole response from a cut one."""
        for attempt, delay in enumerate((*RETRY_DELAYS, None), start=1):
            self._wait_turn()
            try:
                response = self._http.get(url)
            except httpx.TransportError as exc:
                problem = f"{type(exc).__name__}: {exc}"
            else:
                if response.status_code == 200 and complete(response.content):
                    return response
                if response.status_code < 500 and response.status_code not in (200, 429):
                    response.raise_for_status()
                problem = f"HTTP {response.status_code}"
            self.stats["retries"] += 1
            if delay is None:
                raise RuntimeError(f"giving up on {url} after {attempt} attempts ({problem})")
            log.warning("%s for %s, retrying in %ss", problem, url, delay)
            time.sleep(delay)
        raise AssertionError("unreachable")

    def _wait_turn(self) -> None:
        wait = self._last_request + self.min_interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()
