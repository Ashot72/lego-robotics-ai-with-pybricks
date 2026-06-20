@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Run setup.bat first.
    exit /b 1
)

call "%~dp0venv\Scripts\activate.bat"
python host.py -n "Pybricks Hub" --timeout 60 %*
set EXITCODE=%ERRORLEVEL%
exit /b %EXITCODE%
