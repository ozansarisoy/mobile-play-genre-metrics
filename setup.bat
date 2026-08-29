@echo off
REM MPG - Mobile Play Genre Metrics: one-command environment setup (Windows)
cd /d "%~dp0"

echo == MPG setup ==
echo 1/3  Creating virtual environment (.venv)...
python -m venv .venv

echo 2/3  Activating and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q

echo 3/3  Installing dependencies from requirements.txt...
pip install -r requirements.txt -q

echo.
echo Setup complete. Next steps:
echo   .venv\Scripts\activate.bat
echo   run.bat
