@echo off
REM ====================================================================
REM MUTUAL FUND ANALYTICS PLATFORM
REM Windows One-Click Dashboard Launcher
REM ====================================================================

title Mutual Fund Analytics Platform
color 0B

echo ====================================================================
echo MUTUAL FUND ANALYTICS PLATFORM
echo Starting Local Streamlit Analytics Server...
echo ====================================================================
echo.

REM 1. Activate Virtual Environment if present
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment 'venv'...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment '.venv'...
    call .venv\Scripts\activate.bat
)

REM 2. Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found in PATH! Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

REM 3. Check and run orchestrator pipeline if database does not exist
if not exist "db\bluestock_mf.db" (
    echo [INFO] Database not found. Executing master ETL pipeline...
    python run_pipeline.py
    if errorlevel 1 (
        echo [ERROR] Pipeline execution failed!
        pause
        exit /b 1
    )
) else (
    echo [INFO] Database 'db\bluestock_mf.db' verified.
)

REM 4. Launch Streamlit Dashboard via python -m streamlit
echo.
echo ====================================================================
echo Launching Mutual Fund Analytics at http://localhost:8501
echo Press Ctrl+C in this terminal window to stop the application.
echo ====================================================================
echo.

python -m streamlit run app.py

pause
