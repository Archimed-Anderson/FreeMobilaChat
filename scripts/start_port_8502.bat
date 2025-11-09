@echo off
echo.
echo ========================================
echo   FreeMobilaChat - Port 8502
echo   Classification Mistral (Prioritaire)
echo ========================================
echo.
echo [1/3] Arret des processus existants...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo.
echo [2/3] Nettoyage du cache...
echo.
echo [3/3] Demarrage sur port 8502...
echo.
cd /d "%~dp0"
python -m streamlit run streamlit_app/pages/5_Classification_Mistral.py --server.port=8502
pause
