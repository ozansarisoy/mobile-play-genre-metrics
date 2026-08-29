#!/usr/bin/env bash
# MPG — Mobile Play Genre Metrics: one-command environment setup (Linux/macOS)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "== MPG setup =="
echo "1/3  Creating virtual environment (.venv)..."
python3 -m venv .venv

echo "2/3  Activating and upgrading pip..."
source .venv/bin/activate
pip install --upgrade pip -q

echo "3/3  Installing dependencies from requirements.txt..."
pip install -r requirements.txt -q

echo ""
echo "Setup complete. Next steps:"
echo "  source .venv/bin/activate"
echo "  ./run.sh"
echo "or simply:  make run"
