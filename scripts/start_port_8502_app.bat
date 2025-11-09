@echo off
echo.
echo ========================================
echo   FreeMobilaChat - Port 8502
echo   Page Principale: app.py
echo ========================================
echo.
echo [1/3] Arret des processus existants...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo.
echo [2/3] Nettoyage du cache...
echo.
echo [3/3] Demarrage avec app.py sur port 8502...
echo.
cd /d "%~dp0\.."
python -m streamlit run streamlit_app/app.py --server.port=8502
pause

