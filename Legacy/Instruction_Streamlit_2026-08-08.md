# XPS-Deconv — Instruction (2026-08-08)

## 1. Purpose

Streamlit multipage app for XPS deconvolution of Thermo Scientific **VGD** files: import → region crop → baseline → peak fit → session/export. Migrated from `V2.ipynb`.

## 2. How to run

```bash
./install.sh   # once
./run.sh       # http://localhost:8501
```

Windows: `install.bat` / `run.bat`.  
Tests: `./venv/bin/python -m pytest tests/ -q`

## 3. Current tree

```text
app.py
launch.py
install.sh  run.sh  install.bat  run.bat
pages/
  1_Import_VGD.py
  2_Region_crop.py
  3_Baseline.py
  4_Deconvolution.py
  5_Peak_library.py
  6_Sessions_Export.py
  7_Settings.py
src/
  utils/   paths, cancel, i18n
  core/    vgd_parser, models, noise, baseline, region, fitting, known_peaks_default
  db/      sessions_repo (SQLite index)
  services/ import, analysis, session, peak_library
  ui/      session_keys, components/
docs/      DECISIONS.md, AI-deployment/
Legacy/    this Instruction
data/      sessions, peak_library.json, sessions_index.db (runtime)
exports/
tests/
V2.ipynb
```

## 4. Five layers (import rules)

`ui/pages → services → db → core → utils`  
No domain algorithms in Streamlit pages beyond wiring widgets.

## 5. Product decisions

See [docs/DECISIONS.md](../docs/DECISIONS.md). Highlights:

- VGD only; one spectrum / one ROI  
- Default baseline: median noise floor from background windows  
- Peak models: gaussian, lorentzian, voigt, pseudovoigt  
- Sessions: JSON + SQLite index  
- i18n EN/RU  

## 6. Domain notes (XPS)

- BE axis plotted high→low (reversed)  
- Corrected intensity from VGD uses dwell × periods when available  
- Shirley / Tougaard available but user-selected  

## 7. UI map

| Page | Role |
|------|------|
| Home (`app.py`) | Overview |
| Import VGD | Load file, pick spectrum |
| Region crop | Active BE window |
| Baseline | Method + windows + preview |
| Deconvolution | Model, peaks, constraints, fit |
| Peak library | Edit reference BE table |
| Sessions / Export | Save/load, Excel/CSV/PNG |
| Settings | Paths / language |

## 8. Post-v1 stubs

- Batch folder processing  
- SVG export polish  
- Richer plot brush UX if Streamlit selection APIs differ by version  

## 9. AI assistant rules (checklist)

- [ ] Keep algorithms in `src/core`  
- [ ] Init session keys; use pending-key pattern for widget writes  
- [ ] Backup SQLite before destructive deletes  
- [ ] Soft-cancel for long fits  
- [ ] Update this Instruction when public structure changes  

## 10. Changelog

- 2026-08-08: Initial scaffold from `V2.ipynb` + `AI-deployment` kit.
