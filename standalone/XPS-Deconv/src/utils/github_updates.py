"""GitHub Releases update check (Layer 1 — no Streamlit).

Public API only. Configure repo via (first match wins):

1. Environment ``XPS_DECONV_GITHUB_REPO`` (``owner/name``)
2. Root file ``GITHUB_REPO`` (one line ``owner/name``)
3. ``git remote get-url origin`` when available
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from src.utils.paths import ROOT
from src.utils.version import get_version

logger = logging.getLogger(__name__)

USER_AGENT = "XPS-Deconv-updater"
API_TIMEOUT_S = 8.0
PREFERRED_ASSET_SUBSTR = ("standalone", "xps-deconv")


@dataclass(frozen=True)
class ReleaseInfo:
    tag: str
    version: str
    html_url: str
    zip_url: Optional[str]
    zip_name: Optional[str]
    name: str = ""


def parse_semver(text: str) -> tuple[int, int, int]:
    """Parse ``1.2.3`` or ``v1.2.3``; unknown → (0, 0, 0)."""
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", (text or "").strip())
    if not m:
        return (0, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def is_newer(remote: str, local: str) -> bool:
    return parse_semver(remote) > parse_semver(local)


def _normalize_repo(raw: str) -> Optional[str]:
    text = (raw or "").strip()
    if not text or text.startswith("#"):
        return None
    if text.endswith(".git"):
        text = text[:-4]
    if "github.com" in text:
        path = urlparse(text).path.strip("/")
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        return None
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", text):
        return text
    return None


def resolve_github_repo(root: Optional[Path] = None) -> Optional[str]:
    """Return ``owner/name`` or None when not configured."""
    env = _normalize_repo(os.environ.get("XPS_DECONV_GITHUB_REPO", ""))
    if env:
        return env

    base = root or ROOT
    repo_file = base / "GITHUB_REPO"
    if repo_file.is_file():
        try:
            line = repo_file.read_text(encoding="utf-8").splitlines()[0]
        except OSError as exc:
            logger.warning("Could not read GITHUB_REPO: %s", exc)
        else:
            parsed = _normalize_repo(line)
            if parsed:
                return parsed

    try:
        out = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            cwd=str(base),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        )
        parsed = _normalize_repo(out)
        if parsed:
            return parsed
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _pick_zip_asset(assets: list[dict]) -> tuple[Optional[str], Optional[str]]:
    zips = [
        a
        for a in assets
        if isinstance(a, dict)
        and str(a.get("name", "")).lower().endswith(".zip")
        and a.get("browser_download_url")
    ]
    if not zips:
        return None, None

    def score(asset: dict) -> tuple[int, str]:
        name = str(asset.get("name", "")).lower()
        pref = 0
        for i, needle in enumerate(PREFERRED_ASSET_SUBSTR):
            if needle in name:
                pref = len(PREFERRED_ASSET_SUBSTR) - i
                break
        return (-pref, name)

    best = sorted(zips, key=score)[0]
    return str(best["browser_download_url"]), str(best.get("name") or "update.zip")


def fetch_latest_release(repo: str) -> Optional[ReleaseInfo]:
    """GET ``/repos/{repo}/releases/latest``. Returns None on any failure."""
    repo = _normalize_repo(repo) or ""
    if not repo:
        return None
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT_S) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        logger.info("GitHub release check skipped/failed for %s: %s", repo, exc)
        return None
    if not isinstance(payload, dict):
        return None
    tag = str(payload.get("tag_name") or "")
    version = tag.lstrip("vV")
    zip_url, zip_name = _pick_zip_asset(list(payload.get("assets") or []))
    html_url = str(payload.get("html_url") or f"https://github.com/{repo}/releases/latest")
    return ReleaseInfo(
        tag=tag,
        version=version,
        html_url=html_url,
        zip_url=zip_url,
        zip_name=zip_name,
        name=str(payload.get("name") or tag),
    )


@dataclass(frozen=True)
class UpdateStatus:
    configured: bool
    local_version: str
    update_available: bool
    latest: Optional[ReleaseInfo]
    repo: Optional[str]
    message: str = ""


def check_for_update(local_version: Optional[str] = None, root: Optional[Path] = None) -> UpdateStatus:
    """Compare local VERSION to GitHub latest release (network; fail soft)."""
    local = (local_version or get_version()).strip()
    repo = resolve_github_repo(root)
    if not repo:
        return UpdateStatus(
            configured=False,
            local_version=local,
            update_available=False,
            latest=None,
            repo=None,
            message="GitHub repo not configured",
        )
    latest = fetch_latest_release(repo)
    if latest is None:
        return UpdateStatus(
            configured=True,
            local_version=local,
            update_available=False,
            latest=None,
            repo=repo,
            message="Could not reach GitHub or no releases",
        )
    newer = is_newer(latest.version, local)
    return UpdateStatus(
        configured=True,
        local_version=local,
        update_available=newer,
        latest=latest,
        repo=repo,
        message="update available" if newer else "up to date",
    )
