"""VGD import service (Layer 4)."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from src.core.models import SpectrumData
from src.core.vgd_parser import VGDFile, read_vgd


def load_vgd(path: str | Path) -> VGDFile:
    return read_vgd(str(path))


def list_spectrum_labels(vgd: VGDFile) -> List[str]:
    labels = []
    for i, sp in enumerate(vgd.spectra):
        labels.append(f"[{i}] {sp.core_level or vgd.core_level} ({sp.num_points} pts)")
    return labels


def spectrum_from_vgd(vgd: VGDFile, index: int = 0) -> SpectrumData:
    if index < 0 or index >= len(vgd.spectra):
        raise IndexError(f"Spectrum index {index} out of range (n={len(vgd.spectra)})")
    sp = vgd.spectra[index]
    return SpectrumData(
        binding_energy=sp.binding_energy.copy(),
        intensity=sp.corrected_intensity.copy(),
        core_level=sp.core_level or vgd.core_level,
        source_path=vgd.filepath,
        spectrum_index=index,
        metadata={
            "title": sp.title,
            "author": sp.author,
            "source_energy": sp.source_energy,
            "pass_energy": sp.pass_energy,
            "dwell_time": sp.dwell_time,
            "periods": sp.periods,
            "be_start": sp.be_start,
            "be_end": sp.be_end,
        },
    )


def load_spectrum(path: str | Path, index: int = 0) -> Tuple[VGDFile, SpectrumData]:
    vgd = load_vgd(path)
    return vgd, spectrum_from_vgd(vgd, index)
