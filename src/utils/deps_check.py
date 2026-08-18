"""Runtime dependency checks (Layer 1).

Validates imports required to run XPS-Deconv (not dev/test tools).
Used by install scripts, run/launch, and app.py on startup.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

# import_name → pip package name (for pip install hints)
RUNTIME_DEPS: tuple[tuple[str, str], ...] = (
    ("streamlit", "streamlit"),
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("matplotlib", "matplotlib"),
    ("scipy", "scipy"),
    ("lmfit", "lmfit"),
    ("olefile", "olefile"),
    ("openpyxl", "openpyxl"),
    ("plotly", "plotly"),
    ("PIL", "pillow"),
)

# Pip names that used to be required and must be removed from old venvs.
# kaleido launched Chrome on export; choreographer is its v1 helper.
OBSOLETE_PIP_PACKAGES: tuple[str, ...] = (
    "kaleido",
    "choreographer",
)


@dataclass(frozen=True)
class MissingDep:
    import_name: str
    pip_name: str
    error: str


def check_runtime_deps(deps: Sequence[tuple[str, str]] = RUNTIME_DEPS) -> List[MissingDep]:
    """Return missing/failed imports (empty list = OK)."""
    missing: List[MissingDep] = []
    for import_name, pip_name in deps:
        try:
            importlib.import_module(import_name)
        except Exception as exc:  # noqa: BLE001 — report any import failure
            missing.append(MissingDep(import_name, pip_name, str(exc)))
    return missing


def _default_requirements_path() -> Path:
    return Path(__file__).resolve().parents[2] / "requirements.txt"


def freeze_pip_names(python_executable: Optional[str] = None) -> set[str]:
    """Installed distribution names (lowercase) from ``pip freeze``."""
    py = python_executable or sys.executable
    proc = subprocess.run(
        [py, "-m", "pip", "freeze"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return set()
    names: set[str] = set()
    for raw in (proc.stdout or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name = line
        for sep in ("===", "==", ">=", "<=", "~=", "!=", "@"):
            if sep in name:
                name = name.split(sep, 1)[0]
                break
        name = name.strip().lower().replace("_", "-")
        if name:
            names.add(name)
    return names


def prune_obsolete_packages(
    *,
    python_executable: Optional[str] = None,
    obsolete: Sequence[str] = OBSOLETE_PIP_PACKAGES,
) -> list[str]:
    """Uninstall leftover packages (e.g. kaleido). Never raises; returns removed names."""
    py = python_executable or sys.executable
    installed = freeze_pip_names(py)
    to_remove = [p for p in obsolete if p.lower().replace("_", "-") in installed]
    if not to_remove:
        return []
    print("Removing unused packages: " + ", ".join(to_remove), flush=True)
    proc = subprocess.run(
        [py, "-m", "pip", "uninstall", "-y", *to_remove],
        check=False,
    )
    if proc.returncode != 0:
        print(
            "WARNING: could not uninstall " + ", ".join(to_remove),
            file=sys.stderr,
            flush=True,
        )
        return []
    print("Removed unused packages: " + ", ".join(to_remove), flush=True)
    return list(to_remove)


def install_requirements(
    requirements_path: Optional[Path] = None,
    *,
    python_executable: Optional[str] = None,
) -> int:
    """Run ``pip install -r requirements.txt``. Return process exit code."""
    req = Path(requirements_path) if requirements_path else _default_requirements_path()
    if not req.is_file():
        print(f"ERROR: requirements file not found: {req}", file=sys.stderr)
        return 1
    py = python_executable or sys.executable
    print(f"Installing packages from {req.name} …")
    proc = subprocess.run(
        [py, "-m", "pip", "install", "-r", str(req)],
        check=False,
    )
    return int(proc.returncode)


def ensure_runtime_deps(
    *,
    requirements_path: Optional[Path] = None,
    python_executable: Optional[str] = None,
    install_if_missing: bool = True,
) -> List[MissingDep]:
    """Check runtime deps; optionally install from requirements.txt, then re-check.

    Returns still-missing deps (empty list = OK).
    """
    prune_obsolete_packages(python_executable=python_executable)
    missing = check_runtime_deps()
    if not missing:
        return []
    if not install_if_missing:
        return missing

    names = ", ".join(sorted({m.pip_name for m in missing}))
    print(f"Missing packages detected ({names}).")
    code = install_requirements(
        requirements_path,
        python_executable=python_executable,
    )
    if code != 0:
        print("ERROR: pip install failed.", file=sys.stderr)
        return check_runtime_deps() or missing

    # Fresh imports after install (modules may have failed earlier in this process)
    return check_runtime_deps()


def format_cli_message(missing: Iterable[MissingDep]) -> str:
    """Multi-line message for terminal / launch.py."""
    lines = [
        "ERROR: Missing Python packages required by XPS-Deconv:",
        "",
    ]
    for item in missing:
        lines.append(f"  · {item.import_name} ({item.pip_name}): {item.error}")
    lines.extend(
        [
            "",
            "How to fix:",
            "  · macOS/Linux: ./run.sh  (auto-installs from requirements.txt)",
            "  · Windows:     run.bat   (auto-installs from requirements.txt)",
            "  · Or: ./install.sh / install.bat",
            "  · Or activate venv and run: pip install -r requirements.txt",
        ]
    )
    return "\n".join(lines)


def exit_if_missing_cli() -> None:
    """Print and exit with code 1 when deps are missing (for scripts / -m)."""
    prune_obsolete_packages()
    missing = check_runtime_deps()
    if missing:
        print(format_cli_message(missing), file=sys.stderr)
        raise SystemExit(1)


def exit_if_ensure_failed() -> None:
    """Prune obsolete packages, install missing deps, then exit 1 if still missing."""
    missing = ensure_runtime_deps(install_if_missing=True)
    if missing:
        print(format_cli_message(missing), file=sys.stderr)
        raise SystemExit(1)
    print("ok — all runtime dependencies importable")


def guard_app_startup() -> None:
    """Block Streamlit UI when runtime deps are missing."""
    missing = check_runtime_deps()
    if not missing:
        return
    msg = format_cli_message(missing)
    try:
        import streamlit as st

        st.set_page_config(page_title="XPS-Deconv — setup", layout="wide")
        st.error("Missing required Python packages")
        for item in missing:
            st.write(f"**{item.import_name}** (`pip install {item.pip_name}`): {item.error}")
        st.info(
            "Close this window and run **run.sh** / **run.bat** "
            "(they install from requirements.txt), or: `pip install -r requirements.txt`"
        )
        st.stop()
    except Exception:
        print(msg, file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    if "--ensure" in sys.argv:
        exit_if_ensure_failed()
    else:
        missing = check_runtime_deps()
        if missing:
            exit_if_missing_cli()
        print("ok — all runtime dependencies importable")
