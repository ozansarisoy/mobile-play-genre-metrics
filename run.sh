#!/usr/bin/env bash
# MPG — Mobile Play Genre Metrics: launch the app (Linux/macOS)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

streamlit run app.py
