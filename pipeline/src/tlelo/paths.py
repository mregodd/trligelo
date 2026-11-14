"""Filesystem locations shared by the pipeline."""

from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    """Return the repository root (the folder that contains ``data/``).

    ``TLELO_ROOT`` overrides the default, which is derived from this file's location
    (``<root>/pipeline/src/tlelo/paths.py``).
    """
    override = os.environ.get("TLELO_ROOT")
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parents[3]


def data_dir() -> Path:
    return repo_root() / "data"


def raw_cache_dir() -> Path:
    """Downloaded HTML pages (git-ignored)."""
    return data_dir() / "raw" / "tff"


def tff_pages_csv() -> Path:
    return data_dir() / "sources" / "tff_pages.csv"
