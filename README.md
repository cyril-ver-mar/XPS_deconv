# XPS-Deconv

Professional Streamlit app for **Thermo Scientific VGD** XPS spectrum deconvolution.

**Version:** see [`VERSION`](VERSION) (current release tagged in git as `vMAJOR.MINOR.PATCH`).  
**Changelog:** [`CHANGELOG.md`](CHANGELOG.md).

## Agent / architecture kit

See [docs/AI-deployment/](docs/AI-deployment/) — deploy checklist and Streamlit playbooks.  
Product decisions: [docs/DECISIONS.md](docs/DECISIONS.md).

## Requirements

- Python **3.11**
- macOS or Windows

## Install & run

Scripts use a Claude-style terminal UI (colored steps + actionable errors).

```bash
./install.sh   # Python 3.11 venv + deps + smoke test (from scratch)
./run.sh       # Streamlit → http://localhost:8501
```

Windows:

```bat
install.bat
run.bat
```

In-app guide: **Documentation** page (also `docs/USER_GUIDE.md` / `docs/USER_GUIDE_ru.md`).

## Standalone distribution (end users)

**Preferred:** give users only the bootstrapper from [`standalone_version/`](standalone_version/)  
(`install_xps_deconv.sh` or `.bat`+`.ps1`). It downloads the latest GitHub Release zip into the folder where the script is run (after typing `YES`).

Maintainer release assets:

```bash
python scripts/build_standalone.py
python scripts/pack_standalone_release.py
# → dist/XPS-Deconv-standalone-{VERSION}.zip  (attach to GitHub Release)
```

Optional: still zip `standalone/XPS-Deconv/` manually if needed. Recipients need Python 3.11 for `install` / `run` after bootstrap.

## Workflow

1. **Projects & Import** — create/load project, upload many VGDs, choose one spectrum  
2. **Region crop** — ROI; invert X / axis ranges / reset on every plot  
3. **Baseline** — reworked denoise + baseline (demo gallery + ❔ helpers)  
4. **Deconvolution** — peaks (default tolerance 0), R / R², fills, sequence snapshots  
5. **Fit sequence** — compare multiple fits (graphs + tables)  
6. **Interactive workspace** — all-in-one live tuning, grey previous fit, save/recall  
7. **Sessions / Export** — Excel / CSV / PNG  

## Layout

```text
app.py, pages/, launch.py, install.sh|bat, run.sh|bat
src/utils|core|db|services|ui
data/ sessions & peak library (gitignored)
exports/
docs/
Legacy/
tests/
V2.ipynb          # legacy notebook source
```

## Tests

```bash
./venv/bin/python -m pytest tests/ -q
```
