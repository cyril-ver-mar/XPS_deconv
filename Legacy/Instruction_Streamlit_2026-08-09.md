# XPS-Deconv — Instruction (2026-08-09)

## 1. Purpose

Streamlit multipage app for XPS deconvolution of Thermo Scientific **VGD** files: projects → region → baseline/denoise → fit → compare/export. Migrated from `V2.ipynb`.

## 2. How to run

```bash
./install.sh   # once
./run.sh       # http://localhost:8501
```

Windows: `install.bat` / `run.bat`.  
Tests: `./venv/bin/python -m pytest tests/ -q`

## 3. Current tree

```text
app.py, launch.py, install.sh|bat, run.sh|bat
pages/
  1_Import_VGD.py          # projects + multi-VGD upload + pick spectrum
  2_Region_crop.py
  3_Baseline.py            # Preview vs Apply; denoise; method demos
  4_Deconvolution.py
  5_Peak_library.py        # data_editor table
  6_Sessions_Export.py
  7_Settings.py
  8_Fit_sequence.py
  9_Interactive_workspace.py
src/
  utils/   paths, cancel, i18n
  core/    vgd_parser, models, project, noise, baseline, region, fitting, known_peaks_default
  db/      sessions_repo
  services/ import, analysis, session, peak_library, project_service
  ui/      session_keys, project_state, components/
           (plots, spectrum_viewer, help, baseline_demos, sidebar)
docs/      DECISIONS.md, ARCHITECTURE.md, AI-deployment/
Legacy/    Instruction snapshots
data/      projects/, sessions/, peak_library.json (runtime, gitignored)
exports/
tests/
V2.ipynb
```

## 4. Five layers (import rules)

`ui/pages → services → db → core → utils`  
No domain algorithms in Streamlit pages beyond wiring widgets.

## 5. Product decisions

See [docs/DECISIONS.md](../docs/DECISIONS.md). Plot UX playbook: [11_scientific_plots_ux.md](../docs/AI-deployment/TASK_PLAYBOOKS/11_scientific_plots_ux.md).

## 6. Domain notes (XPS)

- BE axis usually high→low (invert X retained without resetting zoom)  
- Corrected intensity from VGD uses dwell × periods when available  
- Shirley / Tougaard available but user-selected  
- RMSE = sqrt(mean(residual²)) from lmfit  

## 7. UI map

| Page | Role |
|------|------|
| Home | Overview |
| Projects & Import | Create/load project; many VGDs; choose active spectrum |
| Region crop | Active BE window |
| Baseline | Denoise + baseline; Preview / Apply; method gallery |
| Deconvolution | Peaks, constraints, fit; metrics + table (no JSON dump) |
| Peak library | Editable table |
| Sessions / Export | Save/load, Excel/CSV/PNG |
| Fit sequence | Compare fit history |
| Interactive workspace | Collapsed panels + live refit + grey previous fit |
| Settings | Paths / language |

## 8. Post-v1 stubs

- Batch folder processing  
- SVG export polish  
- Richer plot brush UX  

## 9. AI assistant rules (checklist)

- [ ] Keep algorithms in `src/core`  
- [ ] Init session keys; pending-key pattern for widget writes  
- [ ] Plot first; collapsed settings; invert retains ranges (playbook 11)  
- [ ] Preview ≠ Apply for baseline  
- [ ] No raw JSON next to tables already shown  
- [ ] Backup SQLite before destructive deletes  
- [ ] Soft-cancel for long fits  
- [ ] Update this Instruction when public structure changes  

## 10. Changelog

- 2026-08-09: Projects, plot UX polish, Preview/Apply baseline, interactive workspace, AI-deployment playbook 11  
- 2026-08-08: Initial scaffold from `V2.ipynb` + `AI-deployment` kit
