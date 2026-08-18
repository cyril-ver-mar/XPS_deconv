"""Tests for runtime dependency guard."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.utils.deps_check import (
    OBSOLETE_PIP_PACKAGES,
    RUNTIME_DEPS,
    MissingDep,
    check_runtime_deps,
    ensure_runtime_deps,
    prune_obsolete_packages,
)


def test_runtime_deps_present_in_venv():
    missing = check_runtime_deps()
    assert not missing, missing


def test_runtime_deps_list_includes_matplotlib_pillow():
    names = {pip for _, pip in RUNTIME_DEPS}
    assert "matplotlib" in names
    assert "pillow" in names
    assert "kaleido" not in names


def test_obsolete_list_includes_kaleido():
    assert "kaleido" in OBSOLETE_PIP_PACKAGES
    assert "choreographer" in OBSOLETE_PIP_PACKAGES


def test_ensure_skips_install_when_ok():
    with patch("src.utils.deps_check.prune_obsolete_packages", return_value=[]), patch(
        "src.utils.deps_check.check_runtime_deps", return_value=[]
    ), patch("src.utils.deps_check.install_requirements") as install:
        assert ensure_runtime_deps() == []
        install.assert_not_called()


def test_ensure_installs_when_missing_then_ok():
    missing = [MissingDep("pillow", "pillow", "No module named 'PIL'")]
    with patch("src.utils.deps_check.prune_obsolete_packages", return_value=[]), patch(
        "src.utils.deps_check.check_runtime_deps",
        side_effect=[missing, []],
    ), patch("src.utils.deps_check.install_requirements", return_value=0) as install:
        assert ensure_runtime_deps(install_if_missing=True) == []
        install.assert_called_once()


def test_ensure_returns_missing_when_install_disabled():
    missing = [MissingDep("pillow", "pillow", "No module named 'PIL'")]
    with patch("src.utils.deps_check.prune_obsolete_packages", return_value=[]), patch(
        "src.utils.deps_check.check_runtime_deps", return_value=missing
    ), patch("src.utils.deps_check.install_requirements") as install:
        assert ensure_runtime_deps(install_if_missing=False) == missing
        install.assert_not_called()


def test_prune_uninstalls_obsolete_when_installed():
    with patch(
        "src.utils.deps_check.freeze_pip_names",
        return_value={"numpy", "kaleido", "streamlit"},
    ), patch("src.utils.deps_check.subprocess.run") as run:
        run.return_value = MagicMock(returncode=0)
        removed = prune_obsolete_packages()
    assert removed == ["kaleido"]
    cmd = run.call_args[0][0]
    assert cmd[1:4] == ["-m", "pip", "uninstall"]
    assert "-y" in cmd
    assert "kaleido" in cmd


def test_prune_skips_when_not_installed():
    with patch("src.utils.deps_check.freeze_pip_names", return_value={"numpy", "pillow"}), patch(
        "src.utils.deps_check.subprocess.run"
    ) as run:
        assert prune_obsolete_packages() == []
        run.assert_not_called()
