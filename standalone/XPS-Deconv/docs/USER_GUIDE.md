# XPS-Deconv — User guide

## 1. Purpose

Deconvolution of Thermo Scientific **VGD** XPS spectra: multi-spectrum projects, ROI crop, baseline, denoise, peak fitting, compare, and export.

## 2. Install & run

### macOS / Linux

```bash
./install.sh
./run.sh
```

### Windows

```bat
install.bat
run.bat
```

If the browser does not open automatically, open http://localhost:8501 or http://127.0.0.1:8501.

## 3. Pages

| Page | Role |
|------|------|
| Home | Overview |
| Import VGD | Project and active spectrum |
| Interactive | All-in-one workspace |
| Region crop | Binding-energy ROI |
| Baseline | Preview and apply |
| Deconvolution | Peaks and fit |
| Fit sequence | Compare fits |
| Peak library | Known peaks |
| Sessions / Export | Save and export |
| Documentation | This guide |
| Settings | Paths and language |

## 4. Typical workflow

1. Import → pick spectrum  
2. Crop ROI  
3. Baseline (Preview → Apply)  
4. Fit peaks  
5. Export  

Use ❔ helpers next to parameters.

## 5. Troubleshooting

| Issue | Fix |
|-------|-----|
| No Python 3.11 | Install 3.11, re-run install |
| No venv | Run install first |
| Port 8501 busy | Stop other Streamlit |
| Browser did not open | Open http://localhost:8501 manually |
