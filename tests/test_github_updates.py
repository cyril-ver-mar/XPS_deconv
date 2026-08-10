"""Tests for GitHub update helpers (offline)."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from src.services.app_updater import apply_standalone_zip
from src.utils.github_updates import (
    _normalize_repo,
    _pick_zip_asset,
    is_newer,
    parse_semver,
    resolve_github_repo,
)


def test_parse_semver() -> None:
    assert parse_semver("v1.0.2") == (1, 0, 2)
    assert parse_semver("1.2.10") == (1, 2, 10)
    assert parse_semver("nope") == (0, 0, 0)


def test_is_newer() -> None:
    assert is_newer("1.0.3", "1.0.2")
    assert not is_newer("1.0.2", "1.0.2")
    assert not is_newer("1.0.1", "1.0.2")


def test_normalize_repo() -> None:
    assert _normalize_repo("acme/XPS-deconvolutor") == "acme/XPS-deconvolutor"
    assert _normalize_repo("https://github.com/acme/XPS-deconvolutor.git") == "acme/XPS-deconvolutor"
    assert _normalize_repo("# comment") is None


def test_resolve_from_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XPS_DECONV_GITHUB_REPO", raising=False)
    (tmp_path / "GITHUB_REPO").write_text("acme/demo-app\n", encoding="utf-8")
    assert resolve_github_repo(tmp_path) == "acme/demo-app"


def test_pick_zip_prefers_standalone() -> None:
    assets = [
        {"name": "source.zip", "browser_download_url": "https://example/a.zip"},
        {
            "name": "XPS-Deconv-standalone-1.0.3.zip",
            "browser_download_url": "https://example/b.zip",
        },
    ]
    url, name = _pick_zip_asset(assets)
    assert url == "https://example/b.zip"
    assert name and "standalone" in name.lower()


def test_apply_preserves_data(tmp_path: Path) -> None:
    app = tmp_path / "app"
    app.mkdir()
    (app / "VERSION").write_text("1.0.2\n", encoding="utf-8")
    (app / "app.py").write_text("OLD\n", encoding="utf-8")
    data = app / "data" / "projects"
    data.mkdir(parents=True)
    keep = data / "mine.json"
    keep.write_text('{"ok": true}\n', encoding="utf-8")

    payload = tmp_path / "upd.zip"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("XPS-Deconv/VERSION", "1.0.3\n")
        zf.writestr("XPS-Deconv/app.py", "NEW\n")
        zf.writestr("XPS-Deconv/src/marker.txt", "x\n")
    payload.write_bytes(buf.getvalue())

    apply_standalone_zip(payload, app_root=app)
    assert (app / "VERSION").read_text(encoding="utf-8").strip() == "1.0.3"
    assert (app / "app.py").read_text(encoding="utf-8").strip() == "NEW"
    assert keep.read_text(encoding="utf-8").startswith("{")
    assert (app / "src" / "marker.txt").is_file()
