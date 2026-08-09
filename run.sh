#!/usr/bin/env bash
# XPS-Deconv launcher — Claude-style terminal UX
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ -t 1 ]] && [[ "${NO_COLOR:-}" == "" ]]; then
  C_ACCENT=$'\033[38;2;217;119;87m'
  C_OK=$'\033[38;2;61;154;110m'
  C_ERR=$'\033[38;2;196;74;74m'
  C_DIM=$'\033[2m'
  C_BOLD=$'\033[1m'
  C_RESET=$'\033[0m'
else
  C_ACCENT=""; C_OK=""; C_ERR=""; C_DIM=""; C_BOLD=""; C_RESET=""
fi

banner() {
  printf '%s\n' "${C_ACCENT}${C_BOLD}"
  cat <<'EOF'
  ╭──────────────────────────────────────────────╮
  │                                              │
  │   XPS-Deconv                                 │
  │   Starting Streamlit…                        │
  │                                              │
  ╰──────────────────────────────────────────────╯
EOF
  printf '%s\n' "${C_RESET}${C_DIM}  http://localhost:8501  ·  Ctrl+C to stop${C_RESET}"
  echo
}

ok() { printf '  %s✓%s %s\n' "$C_OK" "$C_RESET" "$*"; }

fail() {
  local title="$1"
  shift
  echo
  printf '%s╭─ Error ──────────────────────────────────────╮%s\n' "$C_ERR" "$C_RESET"
  printf '%s│%s %-44s %s│%s\n' "$C_ERR" "$C_RESET" "$title" "$C_ERR" "$C_RESET"
  printf '%s╰──────────────────────────────────────────────╯%s\n' "$C_ERR" "$C_RESET"
  if [[ "$#" -gt 0 ]]; then
    echo
    printf '%sHow to fix%s\n' "$C_BOLD" "$C_RESET"
    for line in "$@"; do
      printf '  %s·%s %s\n' "$C_ACCENT" "$C_RESET" "$line"
    done
  fi
  echo
  exit 1
}

banner

if [[ ! -d venv ]]; then
  fail "Virtual environment missing" \
    "Run the installer first: ./install.sh" \
    "Then: ./run.sh"
fi

# shellcheck disable=SC1091
source venv/bin/activate
VPY="$ROOT/venv/bin/python"

if [[ ! -x "$VPY" ]]; then
  fail "venv/bin/python is broken" \
    "rm -rf venv && ./install.sh" \
    "Then: ./run.sh"
fi

if [[ ! -f app.py ]]; then
  fail "app.py not found" \
    "cd into the XPS-Deconv project folder" \
    "Expected: $ROOT/app.py"
fi

if [[ ! -f launch.py ]]; then
  fail "launch.py not found" \
    "Project files may be incomplete — re-clone or restore launch.py"
fi

if ! "$VPY" -c "import streamlit" 2>/dev/null; then
  fail "streamlit is not installed in venv" \
    "./install.sh" \
    "Then: ./run.sh"
fi

ok "venv ready"
ok "streamlit available"
printf '  %s→%s launching…\n' "$C_ACCENT" "$C_RESET"
echo

exec "$VPY" launch.py
