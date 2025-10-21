@echo off
echo ========================================
echo    NETTOYAGE COMPLET ET REDEMARRAGE
echo ========================================
echo.

echo [1/5] Arret de tous les processus Python...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [2/5] Suppression du cache Streamlit...
rmdir /s /q "%USERPROFILE%\.streamlit" 2>nul
rmdir /s /q "streamlit_app\.streamlit\cache" 2>nul
rmdir /s /q ".streamlit\cache" 2>nul

echo.
echo [3/5] Suppression des caches Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo.
echo [4/5] Demarrage du Backend API...
start "Backend API" cmd /k "cd /d %~dp0 && python -m uvicorn app:app --host 0.0.0.0 --port 8000"

echo.
echo [5/5] Demarrage de Streamlit (mode propre)...
cd streamlit_app
python -m streamlit run app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false

echo.
echo ========================================
echo    APPLICATION REDEMARREE !
echo ========================================
echo.
echo IMPORTANT: Dans votre navigateur, appuyez sur Ctrl+F5 pour vider le cache !
echo.
echo URLs:
echo - Page Principale: http://localhost:8501
echo.
pause

