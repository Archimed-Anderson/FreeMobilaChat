@echo off
REM ========================================================================
REM Script de Redémarrage Forcé - Dashboard Version 3.0
REM Force le rechargement complet avec nettoyage cache
REM ========================================================================

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  REDÉMARRAGE FORCÉ - Dashboard Version 3.0                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Étape 1: Arrêter toutes les instances Streamlit
echo [1/5] Arrêt des instances Streamlit...
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *streamlit*" /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo       [✓] Instances arrêtées

REM Étape 2: Nettoyer les caches
echo [2/5] Nettoyage des caches...
rmdir /S /Q "%USERPROFILE%\.streamlit\cache" >nul 2>&1
rmdir /S /Q ".streamlit\cache" >nul 2>&1
rmdir /S /Q "__pycache__" >nul 2>&1
rmdir /S /Q "streamlit_app\__pycache__" >nul 2>&1
rmdir /S /Q "streamlit_app\services\__pycache__" >nul 2>&1
del /F /Q "*.pyc" >nul 2>&1
echo       [✓] Caches nettoyés

REM Étape 3: Vérifier le fichier existe
echo [3/5] Vérification du fichier...
if exist "streamlit_app\pages\5_Classification_Mistral.py" (
    echo       [✓] Fichier trouvé
) else (
    echo       [✗] ERREUR: Fichier non trouvé!
    pause
    exit /b 1
)

REM Étape 4: Afficher la version
echo [4/5] Version du dashboard...
findstr /C:"Version: 3.0" "streamlit_app\pages\5_Classification_Mistral.py" >nul
if %errorlevel%==0 (
    echo       [✓] Version 3.0 détectée
) else (
    echo       [!] Version non détectée
)

REM Étape 5: Relancer Streamlit
echo [5/5] Lancement de Streamlit...
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  Dashboard en cours de démarrage...                        ║
echo ║  URL: http://localhost:8501/Classification_Mistral         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo IMPORTANT:
echo • Le navigateur va s'ouvrir automatiquement
echo • Appuyez sur Ctrl+Shift+R pour forcer le rafraîchissement
echo • Vérifiez que "Version 3.0" s'affiche en haut à droite
echo.
timeout /t 3 /nobreak >nul

REM Lancer Streamlit
cd /d "%~dp0"
python -m streamlit run streamlit_app\pages\5_Classification_Mistral.py --server.headless true --server.runOnSave true

pause

