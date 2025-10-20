@echo off
echo ========================================
echo    FreeMobilaChat - Demarrage Final
echo ========================================
echo.

echo [1/3] Arret des processus existants...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Demarrage du Backend API...
start "Backend API" cmd /k "cd /d %~dp0 && python -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo.
echo [3/3] Demarrage de l'application Streamlit...
cd streamlit_app
python -m streamlit run app.py --server.port 8501

echo.
echo ========================================
echo    Application demarree avec succes !
echo ========================================
echo.
echo URLs FONCTIONNELLES:
echo - Application: http://localhost:8501
echo - Analyse Intelligente: http://localhost:8501/analyse_intelligente
echo - Analyse Classique: http://localhost:8501/analyse_old
echo - Resultats: http://localhost:8501/resultat
echo.
echo Pour tester: python test_app.py
echo.
pause
