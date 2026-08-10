# Changelog

All notable changes to **XPS-Deconv** are listed here.  
Version source of truth: root [`VERSION`](VERSION). Git tags: `vMAJOR.MINOR.PATCH`.

## [1.0.3] — 2026-08-10

### Added
- **GitHub Releases update check** on every app launch (once per session).
- Banner when a newer release exists: version available + link to the release page.
- Optional **Download & install** (confirmation required); keeps `data/`, `exports/`, and `venv/`.
- **Settings → Updates** section with repo status and “Check now”.
- Repo id via `GITHUB_REPO` (`cyril-ver-mar/XPS_deconv`) or env `XPS_DECONV_GITHUB_REPO`.
- `scripts/pack_standalone_release.py` — builds `dist/XPS-Deconv-standalone-{VERSION}.zip` for release assets.
- Standalone package rebuilt and synced with the same update strategy.

### Docs
- User guides and decisions updated for update checking and release packaging.

## [1.0.2] — 2026-08-09

### Added
- **Plot settings → Export graph**: PNG / JPEG / TIFF with size in inches and DPI (Kaleido + Pillow).
- Shared helper `src/ui/components/plot_export.py` and tests.

### Docs
- Plot export documented in DECISIONS, playbook 11, and user guides.

## [1.0.1] — 2026-08-09

### Changed
- Plot legend / margin spacing for clearer overlays.
- Interactive workspace helpers and polish.
- Streamlit telemetry / email prompt off; clearer launch tips for localhost.

### Added
- Semver via root `VERSION` + `src/utils/version.py`.
- Standalone end-user package (`scripts/build_standalone.py` → `standalone/XPS-Deconv/`).

## [1.0.0] — 2026-08-09

### Added
- Initial release: VGD import, projects, region crop, baseline (Preview ≠ Apply), denoise, deconvolution, fit sequence, peak library, interactive workspace, sessions/export, EN/RU UI, in-app documentation.
