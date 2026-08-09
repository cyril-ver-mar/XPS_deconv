#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d venv ]]; then
  echo "Creating venv (Python 3.11)…"
  python3.11 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "Install complete. Run: ./run.sh"
