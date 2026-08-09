# Decisions — XPS-Deconv

**App display name:** XPS-Deconv  
**Last updated:** 2026-08-09

## Locked

| Topic | Decision |
|-------|----------|
| Stack | Python 3.11 + Streamlit multipage |
| Architecture | Five-layer `src/` (`utils` → `core` → `db` → `services` → `ui`) |
| Input | Thermo Scientific **VGD only**; many spectra per **project**; analyse one at a time |
| Region | One active ROI; sliders + presets + numeric; plot invert X / axis ranges / reset |
| Baseline default | Noise-floor median from background windows; gallery demos; user chooses method |
| Baseline UX | **Preview** vs **Apply** (preview does not lock until Apply) |
| Denoise | Reworked: none / median / moving_average / savgol / wiener |
| Peak models | Gaussian, Lorentzian, Voigt, PseudoVoigt/GL(m) — choose before fit |
| Tolerance default | **0** (fixed center) |
| Constraints | Fixed FWHM, linked doublets, shared sigma — on/off + ❔ helpers |
| Fit UX | Trace toggles, fill colors/alpha, R & R² & RMSE, fit sequence compare, interactive workspace |
| Plot UX | Plot first; settings accordion collapsed below; invert X retains ranges; Y fit uses all series |
| Results UI | Metric cards + dataframes only — no raw JSON dumps next to tables |
| Peak library UI | `st.data_editor` table; add/delete core levels; restore defaults |
| Page order | Home → Import → Interactive → analysis → Documentation → Settings |
| In-app docs | `pages/10_Documentation.py` reads `docs/USER_GUIDE(_ru).md` |
| Install UX | `install`/`run` `.sh`/`.bat`: Claude-style banner, steps, actionable errors |
| Interactive UI | Denoise / Baseline / Model / Peaks expanders **collapsed by default**; uncertainty+PV sum panel |
| Storage | JSON projects in `data/projects/` + SQLite index; sessions/exports as before |
| Secrets | None required |
| i18n | English + Russian; **default = Russian** |
| OS | macOS + Windows (`install`/`run` scripts) |
| Packaging | Deferred |
| Kit playbooks | C6 / G4 = yes — scientific plots playbook 11 |

## Deploy from AI-deployment (2026-08-08)

| ID | Choice | Notes |
|----|--------|-------|
| A1 | `/Users/kirillverbilo/JP/PhD/!!!XPS-deconvolutor` | Project-local git (not `$HOME`) |
| A2 | XPS-Deconv | |
| A3 | 3.11 | |
| A4 | yes | Multipage |
| A5 | yes | Git init done |
| B1 | yes | Five-layer |
| B2 | yes | Living Instruction |
| B3 | yes | Code Complete rule |
| C1–C5 | yes | Soft cancel, i18n EN/RU |
| C6 | yes | Scientific plot UX (playbook 11) — locked 2026-08-09 |
| D1 | yes | SQLite index + JSON sessions/projects |
| D2 | yes | Backup before destructive writes |
| D3 | later | Small tables for now |
| E1 | n/a | No API secrets |
| E2 | yes | `venv/`, `data/`, `exports/`, `*.db` |
| E3 | yes | `data/sessions/`, `data/projects/` |
| E4 | console + optional `*.log` | |
| F1 | yes | pytest |
| F2 | later | Polish pipeline |
| F3 | yes | This file |
| F4 | yes | Packaging deferred |
| G1 | no | Not RDKit chem library |
| G4 | yes | Spectroscopy plot pack |
| H1 | yes | General Cursor rules installed |
| H4 | yes | `scientific-plots.mdc` installed |
| Kit path | `docs/AI-deployment/` | Relocated from root |

## Baseline algorithm (locked)

1. Select background windows (auto left/right edges and/or manual intervals).  
2. Take **median** intensity inside windows (robust noise floor).  
3. Build baseline from medians (horizontal / linear through side medians / smooth).  
4. Also offer Shirley, Tougaard, classic linear, polynomial — user chooses.

## Fit statistics (locked)

- **R** — Pearson correlation of data vs best_fit  
- **R²** — \(1 - SS_{res}/SS_{tot}\)  
- **RMSE** — \(\sqrt{\mathrm{mean}(r_i^2)}\) on lmfit residuals  
- **χ²_red** — lmfit reduced chi-square  

## Polish notes (2026-08-09)

See `docs/AI-deployment/TASK_PLAYBOOKS/11_scientific_plots_ux.md` for reusable patterns extracted from this project.
