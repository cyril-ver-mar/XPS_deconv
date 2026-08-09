# XPS-Deconv

Professional Streamlit app for **Thermo Scientific VGD** XPS spectrum deconvolution.

## Agent / architecture kit

See [docs/AI-deployment/](docs/AI-deployment/) — deploy checklist and Streamlit playbooks.  
Product decisions: [docs/DECISIONS.md](docs/DECISIONS.md).

## Requirements

- Python **3.11**
- macOS or Windows

## Install & run

```bash
./install.sh
./run.sh
```

Windows:

```bat
install.bat
run.bat
```

Open http://localhost:8501

## Workflow

1. Import VGD (one spectrum)  
2. Crop region (sliders / presets / numeric / brush)  
3. Baseline (median noise-floor recommended; Shirley / Tougaard / smooth also available)  
4. Deconvolution (Gaussian / Lorentzian / Voigt / PseudoVoigt)  
5. Save session + export Excel / CSV / PNG  

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
