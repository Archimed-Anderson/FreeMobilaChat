# ==============================================================================
# 🚀 Quick Deploy - FreeMobilaChat
# ==============================================================================
# Usage rapide sans prompts
# ==============================================================================

param(
    [string]$Message = "Quick update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
)

Write-Host "🚀 Quick Deploy..." -ForegroundColor Cyan

# Nettoyage rapide
Write-Host "🧹 Nettoyage..." -ForegroundColor Yellow
Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -File -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

# Configuration Git
git config --local core.autocrlf true
git config --local core.safecrlf warn

# Vérifier les modifications
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "✅ Aucune modification à déployer" -ForegroundColor Green
    exit 0
}

# Afficher les modifications
Write-Host "`n📝 Modifications:" -ForegroundColor Yellow
git status --short

# Commit et push
Write-Host "`n💾 Commit..." -ForegroundColor Yellow
git add .
git commit -m $Message

Write-Host "`n⬆️  Push..." -ForegroundColor Yellow
$branch = git branch --show-current
git push origin $branch

Write-Host "`n✅ Déployé sur $branch!" -ForegroundColor Green
git log --oneline -1
