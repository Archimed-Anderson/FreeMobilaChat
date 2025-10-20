@echo off
echo ========================================
echo    FreeMobilaChat - Nettoyage Complet
echo ========================================
echo.

echo [1/6] Arret de tous les processus Python...
taskkill /f /im python.exe 2>nul
timeout /t 3 /nobreak >nul

echo.
echo [2/6] Nettoyage du cache Streamlit utilisateur...
rmdir /s /q "%USERPROFILE%\.streamlit" 2>nul

echo.
echo [3/6] Nettoyage du cache local...
rmdir /s /q "streamlit_app\.streamlit" 2>nul

echo.
echo [4/6] Nettoyage des caches Python...
rmdir /s /q "streamlit_app\__pycache__" 2>nul
rmdir /s /q "streamlit_app\pages\__pycache__" 2>nul
rmdir /s /q "streamlit_app\components\__pycache__" 2>nul
rmdir /s /q "streamlit_app\services\__pycache__" 2>nul

echo.
echo [5/6] Demarrage du Backend API...
start "Backend API" cmd /k "cd /d %~dp0 && python -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo.
echo [6/6] Demarrage de l'application Streamlit...
cd streamlit_app
python -m streamlit run app.py --server.port 8501 --server.headless true

echo.
echo ========================================
echo    Nettoyage termine - Application demarree !
echo ========================================
echo.
echo IMPORTANT: Videz le cache de votre navigateur (Ctrl+F5)
echo.
echo URLs disponibles:
echo - Application: http://localhost:8501
echo - Analyse Intelligente: http://localhost:8501/analyse_intelligente
echo - Analyse Classique: http://localhost:8501/analyse_old
echo - Resultats: http://localhost:8501/resultat
echo.
pause
