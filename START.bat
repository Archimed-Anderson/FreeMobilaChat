@echo off
REM FreeMobilaChat - Quick Start Batch Script
REM Double-click this file to start the application

echo ============================================
echo   FreeMobilaChat - Quick Launcher
echo ============================================
echo.

cd /d "%~dp0"

echo Current Directory: %CD%
echo.

echo Starting Streamlit Application...
echo.
echo The application will open in your browser at:
echo   http://localhost:8502
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run streamlit_app/app.py --server.port 8502 --server.headless false

pause
