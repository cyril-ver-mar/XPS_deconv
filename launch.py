#!/usr/bin/env python3
"""Launch Streamlit XPS-Deconv with clear errors.

On start: prune unused packages, then install from requirements.txt if anything is missing.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _ensure_deps() -> int | None:
    """Install missing packages from requirements.txt. Return exit code on failure."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from src.utils.deps_check import ensure_runtime_deps, format_cli_message

    req = ROOT / "requirements.txt"
    missing = ensure_runtime_deps(
        requirements_path=req,
        python_executable=sys.executable,
        install_if_missing=True,
    )
    if missing:
        print(format_cli_message(missing), file=sys.stderr)
        return 1
    return None


def main() -> int:
    app = ROOT / "app.py"
    if not app.is_file():
        print("ERROR: app.py not found next to launch.py", file=sys.stderr)
        print(f"  Expected: {app}", file=sys.stderr)
        return 1
    dep_err = _ensure_deps()
    if dep_err is not None:
        return dep_err
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("ERROR: streamlit is not installed in this Python environment.", file=sys.stderr)
        print("  Fix: run ./install.sh (macOS/Linux) or install.bat (Windows)", file=sys.stderr)
        print(f"  Python: {sys.executable}", file=sys.stderr)
        return 1

    print()
    print("  If the browser does not open automatically:")
    print("  · open http://localhost:8501 yourself")
    print("  · or try http://127.0.0.1:8501")
    print("  · if the port is busy, stop the other Streamlit and re-run")
    print()

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app),
        "--server.headless",
        "false",
        "--server.showEmailPrompt",
        "false",
        "--browser.gatherUsageStats",
        "false",
    ]
    try:
        return subprocess.call(cmd, cwd=str(ROOT))
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except OSError as exc:
        print(f"ERROR: could not start Streamlit: {exc}", file=sys.stderr)
        print("  Fix: re-run install; check that port 8501 is free", file=sys.stderr)
        print("  Manual URL: http://localhost:8501", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
