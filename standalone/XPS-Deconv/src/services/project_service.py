"""Project persistence (Layer 3 + 4)."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from src.core.project import AnalysisProject, SpectrumEntry
from src.core.models import SpectrumData
from src.utils.paths import DATA_DIR, ensure_runtime_dirs

PROJECTS_DIR = DATA_DIR / "projects"
PROJECT_DB_PATH = DATA_DIR / "projects_index.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    json_path TEXT NOT NULL UNIQUE,
    n_spectra INTEGER DEFAULT 0,
    notes TEXT
);
"""


def ensure_project_dirs() -> None:
    ensure_runtime_dirs()
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def connect(db_path: Optional[Path] = None) -> Iterator[sqlite3.Connection]:
    ensure_project_dirs()
    path = db_path or PROJECT_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def backup_db() -> Optional[Path]:
    ensure_project_dirs()
    if not PROJECT_DB_PATH.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = PROJECT_DB_PATH.with_suffix(f".{stamp}.bak")
    dest.write_bytes(PROJECT_DB_PATH.read_bytes())
    return dest


def project_json_path(project_id: str) -> Path:
    return PROJECTS_DIR / f"{project_id}.json"


def save_project(project: AnalysisProject) -> Path:
    ensure_project_dirs()
    project.touch()
    path = project_json_path(project.id)
    path.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO projects (id, name, created_at, updated_at, json_path, n_spectra, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name=excluded.name,
              updated_at=excluded.updated_at,
              json_path=excluded.json_path,
              n_spectra=excluded.n_spectra,
              notes=excluded.notes
            """,
            (
                project.id,
                project.name,
                project.created_at,
                project.updated_at,
                str(path),
                len(project.spectra),
                project.notes,
            ),
        )
    return path


def load_project(project_id: str) -> AnalysisProject:
    path = project_json_path(project_id)
    if not path.exists():
        # try index path
        with connect() as conn:
            row = conn.execute(
                "SELECT json_path FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
            if not row:
                raise FileNotFoundError(f"Project not found: {project_id}")
            path = Path(row["json_path"])
    return AnalysisProject.from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_projects() -> List[Dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_project(project_id: str) -> None:
    backup_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT json_path FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if row:
            path = Path(row["json_path"])
            if path.exists():
                path.unlink()
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))


def create_project(name: str, notes: str = "") -> AnalysisProject:
    project = AnalysisProject(name=name.strip() or "Untitled project", notes=notes)
    save_project(project)
    return project


def add_spectrum_to_project(
    project: AnalysisProject,
    spectrum: SpectrumData,
    label: Optional[str] = None,
) -> SpectrumEntry:
    entry = SpectrumEntry(
        label=label or f"{spectrum.core_level} [{spectrum.spectrum_index}]",
        spectrum=spectrum,
    )
    project.spectra.append(entry)
    if project.active_spectrum_id is None:
        project.active_spectrum_id = entry.id
    save_project(project)
    return entry


def set_active_spectrum(project: AnalysisProject, spectrum_id: str) -> SpectrumEntry:
    for s in project.spectra:
        if s.id == spectrum_id:
            project.active_spectrum_id = spectrum_id
            save_project(project)
            return s
    raise KeyError(spectrum_id)
