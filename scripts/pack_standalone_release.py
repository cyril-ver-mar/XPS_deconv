#!/usr/bin/env python3
"""Build standalone folder and zip it for a GitHub Release asset.

Usage (from project root):
  python scripts/build_standalone.py
  python scripts/pack_standalone_release.py

Output:
  dist/XPS-Deconv-standalone-{VERSION}.zip
  (attach this zip to the GitHub Release for tag v{VERSION})
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDALONE = ROOT / "standalone" / "XPS-Deconv"
DIST = ROOT / "dist"


def _version() -> str:
    text = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return text.splitlines()[0].strip() or "0.0.0"


def main() -> None:
    if not (STANDALONE / "app.py").is_file():
        raise SystemExit(
            "standalone/XPS-Deconv missing — run: python scripts/build_standalone.py"
        )
    DIST.mkdir(parents=True, exist_ok=True)
    ver = _version()
    out = DIST / f"XPS-Deconv-standalone-{ver}.zip"
    if out.exists():
        out.unlink()

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in STANDALONE.rglob("*"):
            if not path.is_file():
                continue
            parts = set(path.parts)
            if parts & {"__pycache__", ".pytest_cache", ".DS_Store", "venv", ".venv"}:
                continue
            # Do not ship user runtime data from a local test install
            if "data" in path.parts and path.name != ".gitkeep":
                continue
            arc = Path("XPS-Deconv") / path.relative_to(STANDALONE)
            zf.write(path, arcname=str(arc))

    print(f"Release asset ready: {out}")
    print(f"Attach to GitHub Release tag v{ver}")


if __name__ == "__main__":
    main()
