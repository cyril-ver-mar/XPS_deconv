#!/usr/bin/env python3
"""Launch Streamlit XPS-Deconv with clear errors."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    app = ROOT / "app.py"
    if not app.is_file():
        print("ERROR: app.py not found next to launch.py", file=sys.stderr)
        print(f"  Expected: {app}", file=sys.stderr)
        return 1
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("ERROR: streamlit is not installed in this Python environment.", file=sys.stderr)
        print("  Fix: run ./install.sh (macOS/Linux) or install.bat (Windows)", file=sys.stderr)
        print(f"  Python: {sys.executable}", file=sys.stderr)
        return 1

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app),
        "--server.headless",
        "true",
    ]
    try:
        return subprocess.call(cmd, cwd=str(ROOT))
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except OSError as exc:
        print(f"ERROR: could not start Streamlit: {exc}", file=sys.stderr)
        print("  Fix: re-run install; check that port 8501 is free", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
