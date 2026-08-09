"""SQLite session index (Layer 3)."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from src.utils.paths import SESSION_DB_PATH, ensure_runtime_dirs

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    core_level TEXT,
    source_path TEXT,
    json_path TEXT NOT NULL UNIQUE,
    notes TEXT
);
"""


@contextmanager
def connect(db_path: Optional[Path] = None) -> Iterator[sqlite3.Connection]:
    ensure_runtime_dirs()
    path = db_path or SESSION_DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def backup_db(db_path: Optional[Path] = None) -> Optional[Path]:
    ensure_runtime_dirs()
    path = db_path or SESSION_DB_PATH
    if not path.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = path.with_suffix(f".{stamp}.bak")
    dest.write_bytes(path.read_bytes())
    return dest


def upsert_session(
    name: str,
    json_path: Path,
    core_level: str = "",
    source_path: str = "",
    notes: str = "",
) -> int:
    with connect() as conn:
        existing = conn.execute(
            "SELECT id FROM sessions WHERE json_path = ?", (str(json_path),)
        ).fetchone()
        now = datetime.now(timezone.utc).isoformat()
        if existing:
            conn.execute(
                """
                UPDATE sessions
                SET name=?, core_level=?, source_path=?, notes=?, created_at=?
                WHERE id=?
                """,
                (name, core_level, source_path, notes, now, existing["id"]),
            )
            return int(existing["id"])
        cur = conn.execute(
            """
            INSERT INTO sessions (name, created_at, core_level, source_path, json_path, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, now, core_level, source_path, str(json_path), notes),
        )
        return int(cur.lastrowid)


def list_sessions() -> List[Dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM sessions ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_session(session_id: int) -> None:
    backup_db()
    with connect() as conn:
        row = conn.execute(
            "SELECT json_path FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row:
            path = Path(row["json_path"])
            if path.exists():
                path.unlink()
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
