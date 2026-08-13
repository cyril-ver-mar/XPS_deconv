"""Tests for runtime dependency guard."""

from __future__ import annotations

from unittest.mock import patch

from src.utils.deps_check import (
    RUNTIME_DEPS,
    MissingDep,
    check_runtime_deps,
    ensure_runtime_deps,
)


def test_runtime_deps_present_in_venv():
    missing = check_runtime_deps()
    assert not missing, missing


def test_runtime_deps_list_includes_kaleido():
    names = {pip for _, pip in RUNTIME_DEPS}
    assert "kaleido" in names
    assert "pillow" in names


def test_ensure_skips_install_when_ok():
    with patch("src.utils.deps_check.check_runtime_deps", return_value=[]), patch(
        "src.utils.deps_check.install_requirements"
    ) as install:
        assert ensure_runtime_deps() == []
        install.assert_not_called()


def test_ensure_installs_when_missing_then_ok():
    missing = [MissingDep("kaleido", "kaleido", "No module named 'kaleido'")]
    with patch(
        "src.utils.deps_check.check_runtime_deps",
        side_effect=[missing, []],
    ), patch("src.utils.deps_check.install_requirements", return_value=0) as install:
        assert ensure_runtime_deps(install_if_missing=True) == []
        install.assert_called_once()


def test_ensure_returns_missing_when_install_disabled():
    missing = [MissingDep("kaleido", "kaleido", "No module named 'kaleido'")]
    with patch("src.utils.deps_check.check_runtime_deps", return_value=missing), patch(
        "src.utils.deps_check.install_requirements"
    ) as install:
        assert ensure_runtime_deps(install_if_missing=False) == missing
        install.assert_not_called()
