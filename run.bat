@echo off
REM MPG - Mobile Play Genre Metrics: launch the app (Windows)
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
  call .venv\Scripts\activate.bat
)

streamlit run app.py
