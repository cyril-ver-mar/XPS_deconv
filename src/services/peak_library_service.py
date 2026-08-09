"""Editable peak binding-energy library (Layer 4).

On-disk JSON is human-readable:
{
  "C1s": [
    {"name": "C-C / C-H", "be_ev": 284.8},
    ...
  ]
}
Legacy [[name, eV], ...] lists are still accepted on load.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.core.known_peaks_default import KNOWN_PEAKS
from src.utils.paths import PEAK_LIBRARY_PATH, ensure_runtime_dirs

PeakList = List[Tuple[str, float]]
PeakLibrary = Dict[str, PeakList]


def default_library() -> PeakLibrary:
    return deepcopy(KNOWN_PEAKS)


def _parse_peak_item(item: Any) -> Tuple[str, float]:
    if isinstance(item, dict):
        name = item.get("name", item.get("label", ""))
        be = item.get("be_ev", item.get("be", item.get("energy", item.get("eV"))))
        return str(name), float(be)
    if isinstance(item, (list, tuple)) and len(item) >= 2:
        return str(item[0]), float(item[1])
    raise ValueError(f"Unrecognized peak entry: {item!r}")


def library_to_human_json(library: PeakLibrary) -> Dict[str, Any]:
    return {
        core: [{"name": name, "be_ev": float(be)} for name, be in peaks]
        for core, peaks in library.items()
    }


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
        out[core] = [_parse_peak_item(it) for it in items]
    return out


def save_library(library: PeakLibrary, path: Path | None = None) -> Path:
    ensure_runtime_dirs()
    path = path or PEAK_LIBRARY_PATH
    path.write_text(
        json.dumps(library_to_human_json(library), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
