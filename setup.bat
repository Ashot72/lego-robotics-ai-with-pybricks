@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === LegoBoost first-time setup ===
echo Project: %cd%
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found on PATH. Install Python 3.10+ and try again.
    exit /b 1
)

if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment: venv
    python -m venv venv
    if errorlevel 1 exit /b 1s
)

call "%~dp0venv\Scripts\activate.bat"

echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
echo Setup finished.
echo If you have not already: install Pybricks firmware on the Move Hub at code.pybricks.com
echo Then turn on the hub, close the LEGO Boost app, and run: host.bat
echo.
exit /b 0
