@echo off
echo ========================================
echo    FreeMobilaChat - Redemarrage Propre
echo ========================================
echo.

echo [1/4] Arret des processus existants...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/4] Nettoyage du cache Streamlit...
rmdir /s /q "%USERPROFILE%\.streamlit" 2>nul

echo.
echo [3/4] Demarrage du Backend API...
start "Backend API" cmd /k "cd /d %~dp0 && python -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo.
echo [4/4] Demarrage de l'application Streamlit...
cd streamlit_app
streamlit run app.py --server.port 8501 --server.headless true

echo.
echo ========================================
echo    Application redemarree avec succes !
echo ========================================
echo.
echo URLs disponibles:
echo - Backend API: http://localhost:8000
echo - Application: http://localhost:8501
echo - Analyse Intelligente: http://localhost:8501/analyse_intelligente
echo - Analyse Classique: http://localhost:8501/analyse_old
echo - Resultats: http://localhost:8501/resultat
echo.
pause
