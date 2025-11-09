@echo off
echo.
echo ========================================
echo   FreeMobilaChat - Dashboard Moderne
echo ========================================
echo.
echo Demarrage avec Home.py (moderne)...
echo.

cd /d "%~dp0\.."
python -m streamlit run streamlit_app/Home.py --server.port 8501

pause

