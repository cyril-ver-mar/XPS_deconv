"""Editable peak binding-energy library (Layer 4)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Tuple

from src.core.known_peaks_default import KNOWN_PEAKS
from src.utils.paths import PEAK_LIBRARY_PATH, ensure_runtime_dirs

PeakList = List[Tuple[str, float]]
PeakLibrary = Dict[str, PeakList]


def default_library() -> PeakLibrary:
    return deepcopy(KNOWN_PEAKS)


def load_library(path: Path | None = None) -> PeakLibrary:
    ensure_runtime_dirs()
    path = path or PEAK_LIBRARY_PATH
    if not path.exists():
        lib = default_library()
        save_library(lib, path)
        return lib
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: PeakLibrary = {}
    for core, items in raw.items():
        out[core] = [(str(name), float(be)) for name, be in items]
    return out


def save_library(library: PeakLibrary, path: Path | None = None) -> Path:
    ensure_runtime_dirs()
    path = path or PEAK_LIBRARY_PATH
    serializable = {k: [[n, e] for n, e in v] for k, v in library.items()}
    path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
