# Decisions — XPS-Deconv

**App display name:** XPS-Deconv  
**Last updated:** 2026-08-08

## Locked

| Topic | Decision |
|-------|----------|
| Stack | Python 3.11 + Streamlit multipage |
| Architecture | Five-layer `src/` (`utils` → `core` → `db` → `services` → `ui`) |
| Input | Thermo Scientific **VGD only**; one spectrum at a time |
| Region | One active ROI at a time; sliders + presets + numeric + brush |
| Baseline default | Noise-floor median from background windows (auto edges + manual); user may choose linear / poly / smooth / Shirley / Tougaard |
| Peak models | Gaussian, Lorentzian, Voigt, PseudoVoigt/GL(m) — choose before fit |
| Constraints | Fixed FWHM, linked doublets, shared params — on/off toggles |
| Peak library | Editable `KNOWN_PEAKS` (file-backed) |
| Storage | JSON session files in `data/sessions/` + SQLite index; exports in `exports/` |
| Secrets | None required |
| i18n | English + Russian |
| OS | macOS + Windows (`install`/`run` scripts) |
| Packaging | Deferred |

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
| D1 | yes | SQLite index + JSON sessions |
| D2 | yes | Backup before destructive writes |
| D3 | later | Small tables for now |
| E1 | n/a | No API secrets |
| E2 | yes | `venv/`, `data/`, `exports/`, `*.db` |
| E3 | yes | `data/sessions/` |
| E4 | console + optional `*.log` | |
| F1 | yes | pytest |
| F2 | later | Polish pipeline |
| F3 | yes | This file |
| F4 | yes | Packaging deferred |
| G1 | no | Not RDKit chem library |
| H1 | yes | General Cursor rules installed |
| Kit path | `docs/AI-deployment/` | Relocated from root |

## Baseline algorithm (locked)

1. Select background windows (auto left/right edges and/or manual intervals).  
2. Take **median** intensity inside windows (robust noise floor).  
3. Build baseline from medians (horizontal / linear through side medians / smooth).  
4. Also offer Shirley, Tougaard, classic linear, polynomial — user chooses.
