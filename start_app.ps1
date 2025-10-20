# FreeMobilaChat - Script de démarrage PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    FreeMobilaChat - Demarrage" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Demarrage du Backend API..." -ForegroundColor Yellow
Start-Process -FilePath "cmd" -ArgumentList "/k", "cd /d $PWD && python -m uvicorn app:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

Write-Host ""
Write-Host "[2/3] Attente du demarrage du backend (5 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "[3/3] Demarrage de l'application Streamlit..." -ForegroundColor Yellow
Set-Location "streamlit_app"
streamlit run app.py --server.port 8501

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "    Application demarree avec succes !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor White
Write-Host "- Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "- Application: http://localhost:8501" -ForegroundColor White
Write-Host ""
Read-Host "Appuyez sur Entree pour continuer"
