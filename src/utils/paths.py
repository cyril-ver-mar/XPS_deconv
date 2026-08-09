"""Project path helpers (Layer 1)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SESSIONS_DIR = DATA_DIR / "sessions"
PROJECTS_DIR = DATA_DIR / "projects"
EXPORTS_DIR = ROOT / "exports"
FIXTURES_DIR = ROOT / "fixtures"
PEAK_LIBRARY_PATH = DATA_DIR / "peak_library.json"
SESSION_DB_PATH = DATA_DIR / "sessions_index.db"
PROJECT_DB_PATH = DATA_DIR / "projects_index.db"


def ensure_runtime_dirs() -> None:
    for path in (DATA_DIR, SESSIONS_DIR, PROJECTS_DIR, EXPORTS_DIR, FIXTURES_DIR):
        path.mkdir(parents=True, exist_ok=True)
