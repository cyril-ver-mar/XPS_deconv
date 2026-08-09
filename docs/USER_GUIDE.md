# XPS-Deconv — User guide

**App:** XPS-Deconv  
**Audience:** XPS analysts using Thermo Scientific **VGD** files  
**Language:** this file is English; the in-app Documentation page also shows Russian.

---

## 1. Purpose

XPS-Deconv turns Thermo Scientific **VGD** spectra into a reproducible deconvolution workflow:

1. Store many spectra in a **project**  
2. Crop one ROI, estimate **baseline**, optional **denoise**  
3. Fit **Gaussian / Lorentzian / Voigt / PseudoVoigt** peaks  
4. Compare fit sequences, export tables and plots  

Science logic lives in `src/core/`; Streamlit pages only orchestrate UI.

---

## 2. Install & run (from scratch)

### macOS / Linux

```bash
./install.sh    # creates Python 3.11 venv + installs requirements
./run.sh        # launches Streamlit → http://localhost:8501
```

### Windows

```bat
install.bat
run.bat
```

Scripts print colored steps and **actionable errors** (missing Python 3.11, broken venv, failed pip, etc.).

Optional tests:

```bash
./venv/bin/python -m pytest tests/ -q
```

---

## 3. App map (pages)

| Page | What it does |
|------|----------------|
| **Home** | Overview and recommended workflow |
| **Import VGD** | Create/load a **project**, upload many VGDs, pick the active spectrum |
| **Interactive** | All-in-one: denoise, baseline, peaks, refit; grey previous fit; uncertainty + selected PseudoVoigt sum |
| **Region crop** | Set one binding-energy ROI as the active working spectrum |
| **Baseline** | Preview vs Apply baseline; method demos; denoise controls |
| **Deconvolution** | Peak list, constraints, run fit, metrics, main spectrum plot + uncertainty panel |
| **Fit sequence** | Compare successive fit snapshots (R, R², RMSE, overlays) |
| **Peak library** | Edit / add / delete core-level peak types; restore built-in defaults |
| **Sessions / Export** | Save/load analysis sessions; Excel / CSV; graph PNG/JPEG/TIFF from Plot settings |
| **Documentation** | This guide (in-app) |
| **Settings** | Paths, language |

Default UI language is **Russian** (switch in the sidebar).

---

## 4. Typical workflow

1. **Import** — create a project → add VGD files → set active spectrum  
2. **Region** (or Interactive) — crop to the core level of interest  
3. **Baseline** — Preview methods → **Apply** the one you keep  
4. **Deconvolution** or **Interactive** — add peaks from the library (tolerance 0 = fixed center by default) → Run / Refit  
5. **Fit sequence** — compare alternatives  
6. **Export** — tables and figures  

❔ icons explain non-obvious parameters.

---

## 5. Architecture (5 layers)

```text
pages / ui  →  services  →  db  →  core  →  utils
```

| Layer | Path | Role |
|-------|------|------|
| L1 | `src/utils/` | paths, i18n, cancel |
| L2 | `src/core/` | VGD parse, baseline, noise, fitting, local stats — **no Streamlit** |
| L3 | `src/db/` | SQLite session/project index |
| L4 | `src/services/` | import, analysis, projects, peak library, export |
| L5 | `src/ui/`, `pages/` | Streamlit presentation only |

---

## 6. Science notes (short)

- **Baseline default idea:** noise-floor **median** in background windows (also Shirley, Tougaard, …).  
- **Preview ≠ Apply** on Baseline.  
- **Tolerance = 0** → peak center fixed unless you raise tolerance / unfix.  
- **Fit stats:** R (Pearson), R², RMSE, χ²_red (lmfit).  
- **Uncertainty panel:** black = data, red = local mean, green = ±n·local σ; purple = sum of **selected** peaks; % = share of points with \|data − sum\| ≤ n·σ.  

Details: `docs/DECISIONS.md`.

---

## 7. Data on disk

| Path | Contents |
|------|----------|
| `data/projects/` | JSON projects (spectra + analysis state) |
| `data/sessions/` | Saved sessions |
| `data/` SQLite index | Project/session listing |
| `exports/` | Excel / CSV / PNG |
| Peak library JSON | Editable known peaks (restorable defaults) |

Do not commit `venv/`, secrets, or bulky runtime data.

---

## 8. Troubleshooting

| Symptom | What to try |
|---------|-------------|
| `Python 3.11 not found` | Install 3.11; on Windows use `py -3.11`; on macOS `brew install python@3.11` |
| `venv missing` | Run `install.sh` / `install.bat` first |
| `pip install failed` | Check network; upgrade pip; retry install script |
| Port 8501 busy | Stop the other Streamlit, or set `STREAMLIT_SERVER_PORT` |
| Import errors after pull | Re-run install to refresh dependencies |
| Plot Y range wrong after fit | Use **Fit all data in view** under Plot settings |
| Need publication figure | **Plot settings → Export graph**: PNG / JPEG / TIFF, inches + DPI |

---

## 9. For AI / developers

- Follow `.cursor/rules/` and `docs/AI-deployment/ARCHITECTURE.md`  
- Living snapshot: `Legacy/Instruction_Streamlit_*.md`  
- Do not invent product rules — update `docs/DECISIONS.md` when the user locks a choice  
