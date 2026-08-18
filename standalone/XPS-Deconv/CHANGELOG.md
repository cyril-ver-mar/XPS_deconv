# Changelog

All notable changes to **XPS-Deconv** are listed here.  
Version source of truth: root [`VERSION`](VERSION). Git tags: `vMAJOR.MINOR.PATCH`.

## [1.0.7] — 2026-08-18

### Added
- **Plot settings → Style**: live preview for fonts, axis names, colors, line widths, grid (major + minor).
- **Plot settings → Export**: PNG / JPEG / TIFF via matplotlib (no Chrome/Kaleido); export matches preview styling.
- **Element BE region overlays** with per-band color and label above the band.
- Optional **compact Y-axis ticks** (25k-style); off by default (full numbers for Russian UI).
- **Peak BE labels** at component maxima with configurable decimal digits (Deconvolution / Interactive).
- Full **EN/RU i18n** for pages, plot legends, axis defaults, and help texts.
- **Update-check failure banner** with typed messages (network, timeout, SSL, HTTP) on launch and in Settings.
- **`OBSOLETE_PIP_PACKAGES`**: auto-uninstall kaleido/choreographer on launch/install.

### Fixed
- **Stale baseline/fit curves** when switching active spectrum — overlays cleared and length-checked.
- Plot export fonts, grid, and proportions aligned with Streamlit preview.

### Changed
- Kaleido removed from runtime dependencies; raster export is matplotlib-only.

## [1.0.6] — 2026-08-13

### Added
- **`src/utils/deps_check.py`** — single runtime dependency guard (incl. kaleido, pillow, matplotlib, openpyxl).
- **`run.sh` / `run.bat`** — on launch, verify all runtime packages and auto `pip install -r requirements.txt` if anything is missing.
- **`launch.py`** — same ensure step before starting Streamlit.
- **`app.py`** — startup guard with a clear error page if packages are still missing.
- **`install.sh` / `install.bat`** — smoke test uses full deps list (not only streamlit/numpy/…).

### Fixed
- Users with an old venv (no kaleido) no longer hit plot-export errors mid-session; re-run **run** or **install** to pull missing packages.

## [1.0.5] — 2026-08-10

### Added
- **4d-metal peak library** defaults: Y3d, Zr3d, Nb3d, Mo3d, Tc3d, Ru3d, Rh3d, Pd3d, Cd3d (metal + common oxides); Ag3d oxide states expanded.
- Matching **region presets** for those 3d windows.
- Bootstrapper asks for install folder path (rejects Temp).

## [1.0.4] — 2026-08-10

### Added
- **One-file bootstrapper** in `standalone_version/` (`install_xps_deconv.sh` / `.bat`+`.ps1`): downloads latest GitHub Release zip into the script’s folder after typing `YES`, then tips for `install` / `run`.

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
