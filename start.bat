@echo off
REM ============================================================
REM  Sichuan Travel - one-click launcher
REM  Python priority: project .venv  >  python on PATH  >  py -3
REM  (ASCII-only messages to avoid console codepage issues)
REM ============================================================

cd /d "%~dp0backend"

REM ---- 1. Locate Python interpreter ----
set "PY_EXE="
set "PY_ARGS="
if exist "%~dp0.venv\Scripts\python.exe" set "PY_EXE=%~dp0.venv\Scripts\python.exe"
if not defined PY_EXE (
    python --version >nul 2>&1 && set "PY_EXE=python"
)
if not defined PY_EXE (
    py -3 --version >nul 2>&1 && set "PY_EXE=py" && set "PY_ARGS=-3"
)
if not defined PY_EXE (
    echo [ERROR] Python not found. Please install Python 3.x first.
    echo         Remember to check "Add Python to PATH" during install.
    echo         Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo [INFO] Using Python:
"%PY_EXE%" %PY_ARGS% --version

REM ---- 2. Check backend\.env ----
if not exist ".env" (
    echo [WARN] backend\.env not found.
    echo        Copy .env.example to .env and fill in AI_API_KEY.
    echo.
)

REM ---- 3. Ensure dependencies are installed (auto-install on first run) ----
"%PY_EXE%" %PY_ARGS% -c "import flask, flask_cors, mysql.connector, jwt, docx, openai, dotenv" >nul 2>&1
if errorlevel 1 (
    echo [INFO] First run: installing dependencies from requirements.txt ...
    "%PY_EXE%" %PY_ARGS% -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed. Check network and run manually:
        echo         "%PY_EXE%" %PY_ARGS% -m pip install -r "%~dp0requirements.txt"
        echo.
        pause
        exit /b 1
    )
    echo [INFO] Dependencies installed.
)

echo ========================================
echo  Sichuan Travel backend starting...
echo  Home:     http://localhost:3000
echo  AI guide: http://localhost:3000/travel-tips.html
echo  Press Ctrl+C to stop.
echo ========================================
echo.

"%PY_EXE%" %PY_ARGS% app.py

echo.
echo Server stopped. Press any key to close this window.
pause >nul
