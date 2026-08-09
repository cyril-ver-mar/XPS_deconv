"""Application version helpers (Layer 1).

Single source of truth: repository root ``VERSION`` file (semver: MAJOR.MINOR.PATCH).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from src.utils.paths import ROOT


@lru_cache(maxsize=1)
def get_version() -> str:
    """Return the app version string from ``VERSION`` (fallback ``0.0.0``)."""
    path = ROOT / "VERSION"
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0"
    return text.splitlines()[0].strip() if text else "0.0.0"


def version_label() -> str:
    """Human-readable label, e.g. ``XPS-Deconv 1.0.1``."""
    return f"XPS-Deconv {get_version()}"
