# XPS-Deconv — one-file installer (bootstrap)

Share **only** these files with end users (not the whole project):

| File | Platform |
|------|----------|
| `install_xps_deconv.sh` | macOS / Linux |
| `install_xps_deconv.bat` + `install_xps_deconv.ps1` | Windows (keep both together) |

## What it does

1. Shows a **warning** and asks you to type `YES`
2. Installs into the **same folder** where the script lives
3. Downloads the **latest** GitHub Release zip (`XPS-Deconv-standalone-*.zip`)
4. Unpacks to `XPS-Deconv/` (keeps existing `data/`, `exports/`, `venv/` on re-run)
5. Prints how to run `install` / `run`

Repo: `cyril-ver-mar/XPS_deconv` (override with env `XPS_DECONV_GITHUB_REPO`).

## macOS / Linux

1. Put `install_xps_deconv.sh` in the folder where you want the app  
2. Open Terminal, `cd` to that folder  
3. Run:
   ```bash
   chmod +x install_xps_deconv.sh
   ./install_xps_deconv.sh
   ```
4. Type `YES`  
5. Then:
   ```bash
   cd XPS-Deconv
   ./install.sh
   ./run.sh
   ```

## Windows

1. Put `install_xps_deconv.bat` **and** `install_xps_deconv.ps1` in the target folder  
2. Double-click `install_xps_deconv.bat` (or run it from cmd)  
3. Type `YES`  
4. Then in cmd:
   ```bat
   cd XPS-Deconv
   install.bat
   run.bat
   ```

Browser: http://localhost:8501

## Maintainer note

Each GitHub Release must attach `dist/XPS-Deconv-standalone-{VERSION}.zip`  
(from `python scripts/build_standalone.py` + `python scripts/pack_standalone_release.py`).
