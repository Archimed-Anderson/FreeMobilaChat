@echo off
echo.
echo ========================================
echo   FreeMobilaChat - Page Originale
echo ========================================
echo.
echo Demarrage avec app.py (authentification)...
echo.

cd /d "%~dp0\.."
python -m streamlit run streamlit_app/app.py --server.port 8501

pause

