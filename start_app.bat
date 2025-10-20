@echo off
echo ========================================
echo    FreeMobilaChat - Demarrage
echo ========================================
echo.

echo [1/3] Demarrage du Backend API...
start "Backend API" cmd /k "cd /d %~dp0 && python -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo.
echo [2/3] Attente du demarrage du backend (5 secondes)...
timeout /t 5 /nobreak > nul

echo.
echo [3/3] Demarrage de l'application Streamlit...
cd streamlit_app
streamlit run app.py --server.port 8501

echo.
echo ========================================
echo    Application demarree avec succes !
echo ========================================
echo.
echo URLs disponibles:
echo - Backend API: http://localhost:8000
echo - Application: http://localhost:8501
echo.
pause
