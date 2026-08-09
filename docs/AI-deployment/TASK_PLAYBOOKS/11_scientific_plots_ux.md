# Playbook 11 — Scientific plots & dense analysis UX

Harvested from XPS-Deconv polish (projects with multi-trace spectra, baselines, fits).  
Ask via `DEPLOY_CHECKLIST` **C6 / G3 (spectroscopy plots)** before adopting wholesale.

## When to use

- Streamlit apps that show **1D spectra / chromatograms / curves** with overlays  
- Users iterate: preview vs apply, toggle traces, zoom, invert axes  
- Dense side panels would otherwise hide the graph  

## Goals

1. Graph is the primary surface — controls stay out of the way  
2. Axis / trace settings **survive** invert, toggle, and page reruns  
3. Preview experimental processing without locking session state  
4. Prefer **tables + metrics** over raw JSON dumps in the UI  

---

## 1. Shared spectrum viewer (L5)

Put plotting in `src/ui/components/` (e.g. `spectrum_viewer.py` + `plots.py`):

| Concern | Pattern |
|---------|---------|
| Build figure | Pure helper (`spectrum_figure`) — no Streamlit |
| Widget chrome | `render_spectrum_viewer(...)` — Streamlit only |
| View state | `PlotViewState` + keyed `session_state` (`{viewer}_xmin`, …) |
| Init once | Flag `{viewer}_ranges_initialized` — **never** reset on invert / trace toggle; if flag is set but a key is missing, **repair** with setdefault only |
| Y bounds | On first init / “Fit all data”, use **all** series (raw, baseline, corrected, fit, components), not raw alone |
| Invert X | Compact control **outside** the settings accordion; must not clear ranges |
| Dense settings | Collapsed `st.expander("Plot settings", expanded=False)` **below** the plot |
| Trace toggles | Checkboxes with stable keys; no `value=` after first seed (avoids reset fights) |
| Plotly | Constant `uirevision` per viewer; enforce stored axis ranges every redraw |

### Anti-patterns

- Putting invert + axis numbers + toggles above the plot (steals first viewport)  
- Re-seeding xmin/xmax/ymin/ymax whenever any checkbox changes  
- Nesting critical editors under `if pending_delete:` / one-shot branches (they vanish)  
- Dumping full metrics/peak JSON with `st.code` / `st.json` when a table already exists  

---

## 2. Preview vs Apply (processing steps)

For baseline / denoise / similar pipelines:

1. **Preview** → write `preview_*` arrays + settings (do not mutate applied session/project yet)  
2. **Apply** → recompute from current widgets → copy into applied keys + persist project  
3. Plot prefers `preview_*` when present, else applied  
4. Optional **Clear preview**  

Caption should say whether the user is viewing preview or applied.

---

## 3. Parameter helpers (❔)

- Short EN/RU (or project i18n) blurbs in `src/ui/components/help.py`  
- `labeled_help(title, key)` + `st.popover("❔")` next to non-obvious parameters  
- Method galleries: synthetic demo curves for each algorithm (e.g. baseline methods) in a collapsed expander  

---

## 4. Dense workspace layout

Interactive / “all-in-one” pages:

- Left column: **collapsed expanders** by default (Denoise, Baseline, Peaks, …)  
- Right column: plot + metrics  
- Peak editors: expanders **collapsed**; Delete / Clear all / Add from library  
- Fit sequence: keep history; overlay selected runs; load one into session  

---

## 5. Human data in UI vs on disk

| Surface | Prefer |
|---------|--------|
| Peak library page | `st.data_editor` table (name, energy) |
| Fit results | Metric cards (R, R², RMSE, χ²) + `st.dataframe` |
| On-disk JSON | Indent + list-of-objects (`{"name", "be_ev"}`, peak records) for reloadable files — **not** shown as primary UI |

---

## 6. Projects with many spectra

- Reloadable **project** JSON + SQLite index  
- Upload many files; **one active spectrum** for analysis  
- Persist per-spectrum work state (region, baseline, peaks, fit history) when switching  

---

## 7. Checklist for agents

- [ ] Plot first; settings accordion below, collapsed  
- [ ] Invert X does not reset ranges / traces  
- [ ] Axis init uses all overlaid series  
- [ ] Preview ≠ Apply for destructive or committing steps  
- [ ] ❔ helpers on non-obvious parameters  
- [ ] No duplicate JSON dumps next to tables  
- [ ] Interactive panels collapsed by default  
- [ ] Peak/list editors never nested under one-shot `if` branches  

## Reference implementation

This repo: `src/ui/components/spectrum_viewer.py`, `plots.py`, `help.py`, `baseline_demos.py`; pages Baseline / Deconvolution / Interactive workspace.
