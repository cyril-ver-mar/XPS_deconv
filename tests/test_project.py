"""Tests for project persistence."""

from __future__ import annotations

import numpy as np

from src.core.models import SpectrumData
from src.services import project_service


def test_project_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(project_service, "PROJECTS_DIR", tmp_path / "projects")
    monkeypatch.setattr(project_service, "PROJECT_DB_PATH", tmp_path / "projects.db")
    project_service.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    proj = project_service.create_project("UnitTest")
    be = np.linspace(290, 280, 40)
    y = np.ones_like(be)
    project_service.add_spectrum_to_project(
        proj, SpectrumData(be, y, core_level="C1s"), label="c1s"
    )
    loaded = project_service.load_project(proj.id)
    assert loaded.name == "UnitTest"
    assert len(loaded.spectra) == 1
    assert loaded.spectra[0].label == "c1s"
    assert loaded.active_spectrum_id == loaded.spectra[0].id
