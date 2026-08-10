#!/usr/bin/env bash
# XPS-Deconv one-file bootstrapper — downloads the latest GitHub Release zip
# into the folder that contains THIS script (not your home directory unless you put it there).
set -euo pipefail

REPO="${XPS_DECONV_GITHUB_REPO:-cyril-ver-mar/XPS_deconv}"
APP_DIR_NAME="XPS-Deconv"
PRESERVE=("data" "exports" "venv" ".venv")

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# --- colors --------------------------------------------------------------
if [[ -t 1 ]] && [[ "${NO_COLOR:-}" == "" ]]; then
  C_ACCENT=$'\033[38;2;217;119;87m'
  C_OK=$'\033[38;2;61;154;110m'
  C_ERR=$'\033[38;2;196;74;74m'
  C_WARN=$'\033[38;2;196;140;40m'
  C_DIM=$'\033[2m'
  C_BOLD=$'\033[1m'
  C_RESET=$'\033[0m'
else
  C_ACCENT=""; C_OK=""; C_ERR=""; C_WARN=""; C_DIM=""; C_BOLD=""; C_RESET=""
fi

ok() { printf '  %s✓%s %s\n' "$C_OK" "$C_RESET" "$*"; }
fail() {
  echo
  printf '%s╭─ Error ──────────────────────────────────────╮%s\n' "$C_ERR" "$C_RESET"
  printf '%s│%s %s\n' "$C_ERR" "$C_RESET" "$1"
  shift || true
  for line in "$@"; do
    printf '  %s·%s %s\n' "$C_ACCENT" "$C_RESET" "$line"
  done
  echo
  exit 1
}

banner() {
  printf '%s\n' "${C_ACCENT}${C_BOLD}"
  cat <<'EOF'
  ╭──────────────────────────────────────────────╮
  │   XPS-Deconv                                 │
  │   Bootstrap — download latest from GitHub    │
  ╰──────────────────────────────────────────────╯
EOF
  printf '%s\n' "${C_RESET}"
}

banner

echo
printf '%s%sWARNING / ПРЕДУПРЕЖДЕНИЕ%s\n' "$C_WARN" "$C_BOLD" "$C_RESET"
echo
echo "  This script will download and install XPS-Deconv"
echo "  INTO THE FOLDER WHERE THIS SCRIPT IS LOCATED:"
printf '  %s%s%s\n' "$C_BOLD" "$SCRIPT_DIR" "$C_RESET"
echo
echo "  Этот скрипт скачает и установит XPS-Deconv"
echo "  В ТУ ЖЕ ПАПКУ, ГДЕ ЛЕЖИТ ЭТОТ ФАЙЛ:"
printf '  %s%s%s\n' "$C_BOLD" "$SCRIPT_DIR" "$C_RESET"
echo
echo "  • Creates / updates:  ${APP_DIR_NAME}/"
echo "  • Keeps (if present):  data/, exports/, venv/"
echo "  • Needs: network + Python 3.11 later for ./install.sh"
echo
printf '  Type %sYES%s to continue (anything else cancels): ' "$C_BOLD" "$C_RESET"
read -r CONFIRM
if [[ "$CONFIRM" != "YES" ]]; then
  echo
  echo "  Cancelled. Move this .sh to the folder where you want the app, then run again."
  echo "  Отменено. Переложите .sh в нужную папку и запустите снова."
  echo
  exit 0
fi

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing command: $1" "Install it, then re-run this script"
}

need_cmd curl
need_cmd unzip
need_cmd python3

TMP="$(mktemp -d "${TMPDIR:-/tmp}/xps_deconv_boot.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo
printf '%s[1/4]%s Resolve latest GitHub Release…\n' "$C_ACCENT" "$C_RESET"
API="https://api.github.com/repos/${REPO}/releases/latest"
JSON="$TMP/release.json"
HTTP_CODE="$(curl -sS -L -A "XPS-Deconv-bootstrap" -H "Accept: application/vnd.github+json" \
  -o "$JSON" -w "%{http_code}" "$API" || true)"
if [[ "$HTTP_CODE" != "200" ]]; then
  fail "GitHub API failed (HTTP $HTTP_CODE)" \
    "Check https://github.com/${REPO}/releases" \
    "Repo must be public, or set XPS_DECONV_GITHUB_REPO=owner/name"
fi

META_OUT="$TMP/meta.txt"
python3 - "$JSON" "$META_OUT" <<'PY' || fail "No .zip asset on the latest release" \
  "Attach XPS-Deconv-standalone-*.zip to the GitHub Release" \
  "https://github.com/${REPO}/releases"
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
assets = data.get("assets") or []
zips = [a for a in assets if str(a.get("name", "")).lower().endswith(".zip") and a.get("browser_download_url")]
if not zips:
    raise SystemExit(2)

def score(a):
    n = str(a.get("name", "")).lower()
    pref = 0
    for i, needle in enumerate(("standalone", "xps-deconv")):
        if needle in n:
            pref = 10 - i
            break
    return (-pref, n)

zips.sort(key=score)
with open(sys.argv[2], "w", encoding="utf-8") as out:
    out.write(zips[0]["browser_download_url"] + "\n")
    out.write((zips[0].get("name") or "update.zip") + "\n")
    out.write((data.get("tag_name") or "") + "\n")
PY

ZIP_URL="$(sed -n '1p' "$META_OUT")"
ZIP_NAME="$(sed -n '2p' "$META_OUT")"
TAG="$(sed -n '3p' "$META_OUT")"
ok "Latest release: ${TAG:-unknown}"
ok "Asset: ${ZIP_NAME}"

echo
printf '%s[2/4]%s Download package…\n' "$C_ACCENT" "$C_RESET"
ZIP_PATH="$TMP/pkg.zip"
curl -sS -L -A "XPS-Deconv-bootstrap" -o "$ZIP_PATH" "$ZIP_URL" \
  || fail "Download failed" "Check network / GitHub status"
ok "Downloaded ($(wc -c < "$ZIP_PATH" | tr -d ' ') bytes)"

echo
printf '%s[3/4]%s Unpack into %s/%s …\n' "$C_ACCENT" "$C_RESET" "$SCRIPT_DIR" "$APP_DIR_NAME"
EXTRACT="$TMP/extract"
mkdir -p "$EXTRACT"
unzip -q "$ZIP_PATH" -d "$EXTRACT"

# Prefer folder that contains app.py + VERSION
SRC="$(python3 - "$EXTRACT" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
cands = []
for app in root.rglob("app.py"):
    if (app.parent / "VERSION").is_file():
        cands.append(app.parent)
if not cands:
    raise SystemExit(2)
cands.sort(key=lambda p: len(p.parts))
print(cands[0])
PY
)" || fail "Zip does not contain app.py + VERSION"

DEST="$SCRIPT_DIR/$APP_DIR_NAME"
mkdir -p "$DEST"

# Preserve user runtime dirs
HOLD="$TMP/preserve"
mkdir -p "$HOLD"
for name in "${PRESERVE[@]}"; do
  if [[ -e "$DEST/$name" ]]; then
    mv "$DEST/$name" "$HOLD/$name"
    ok "Preserved $name"
  fi
done

# Replace app files (remove old non-preserved content)
# Keep DEST itself; wipe then copy
find "$DEST" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
cp -R "$SRC"/. "$DEST"/

for name in "${PRESERVE[@]}"; do
  if [[ -e "$HOLD/$name" ]]; then
    rm -rf "$DEST/$name"
    mv "$HOLD/$name" "$DEST/$name"
  fi
done
ok "Installed to $DEST"
if [[ -f "$DEST/VERSION" ]]; then
  ok "VERSION $(tr -d '\r' < "$DEST/VERSION" | head -n1)"
fi

echo
printf '%s[4/4]%s Next steps\n' "$C_ACCENT" "$C_RESET"
echo
printf '%sHow to finish setup and run%s\n' "$C_BOLD" "$C_RESET"
echo
echo "  1. Open Terminal"
echo "  2. Go to the app folder:"
printf '     %scd "%s"%s\n' "$C_BOLD" "$DEST" "$C_RESET"
echo "  3. First time only — install Python deps:"
printf '     %s./install.sh%s\n' "$C_BOLD" "$C_RESET"
echo "  4. Start the app:"
printf '     %s./run.sh%s\n' "$C_BOLD" "$C_RESET"
echo
echo "  Browser: http://localhost:8501  (or http://127.0.0.1:8501)"
echo
echo "  Как запустить:"
echo "  1. Откройте Терминал"
echo "  2. cd в папку приложения (команда выше)"
echo "  3. ./install.sh   (один раз)"
echo "  4. ./run.sh"
echo
ok "Bootstrap finished."
echo
