# ==============================================================================
# 🚀 Script de Déploiement FreeMobilaChat - Windows PowerShell
# ==============================================================================
# Version: 1.0
# Auteur: AI DevOps Engineer
# Compatible: Windows 10/11 avec PowerShell 5.1+
# ==============================================================================

Write-Host "🚀 Déploiement FreeMobilaChat - Démarrage" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Gray

# ==============================================================================
# 1. NETTOYAGE DES FICHIERS TEMPORAIRES
# ==============================================================================
Write-Host "`n🧹 Étape 1/9: Nettoyage des fichiers temporaires..." -ForegroundColor Yellow

# Supprimer __pycache__
Get-ChildItem -Path . -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Supprimé: $($_.FullName)" -ForegroundColor DarkGray
}

# Supprimer *.pyc
Get-ChildItem -Path . -File -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
}

# Supprimer .DS_Store (macOS)
Get-ChildItem -Path . -File -Recurse -Filter ".DS_Store" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
}

Write-Host "  ✅ Nettoyage terminé" -ForegroundColor Green

# ==============================================================================
# 2. CONFIGURATION STREAMLIT
# ==============================================================================
Write-Host "`n⚙️  Étape 2/9: Configuration de Streamlit..." -ForegroundColor Yellow

# Créer les répertoires
New-Item -Path ".streamlit" -ItemType Directory -Force | Out-Null
New-Item -Path "streamlit_app\.streamlit" -ItemType Directory -Force | Out-Null

# Créer le fichier de configuration
$streamlitConfig = @"
[server]
port = 8501
headless = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#1E3A5F"
"@

Set-Content -Path ".streamlit\config.toml" -Value $streamlitConfig -Encoding UTF8
Copy-Item -Path ".streamlit\config.toml" -Destination "streamlit_app\.streamlit\config.toml" -Force

Write-Host "  ✅ Configuration Streamlit créée" -ForegroundColor Green

# ==============================================================================
# 3. CONFIGURATION GIT
# ==============================================================================
Write-Host "`n🔄 Étape 3/9: Configuration Git..." -ForegroundColor Yellow

# Configuration Git pour Windows
git config --local core.autocrlf true
git config --local core.safecrlf warn
git config --local core.filemode false

Write-Host "  ✅ Git configuré" -ForegroundColor Green

# ==============================================================================
# 4. VÉRIFICATION DES FICHIERS ESSENTIELS
# ==============================================================================
Write-Host "`n📝 Étape 4/9: Vérification des fichiers essentiels..." -ForegroundColor Yellow

$essentialFiles = @(
    "requirements-academic.txt",
    "README.md",
    ".gitignore",
    "streamlit_app\Home.py"
)

$allFilesExist = $true
foreach ($file in $essentialFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor DarkGray
    } else {
        Write-Host "  ✗ MANQUANT: $file" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if ($allFilesExist) {
    Write-Host "  ✅ Tous les fichiers essentiels présents" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Certains fichiers manquent" -ForegroundColor Yellow
}

# ==============================================================================
# 5. STATUS GIT ACTUEL
# ==============================================================================
Write-Host "`n🔍 Étape 5/9: Status Git actuel..." -ForegroundColor Yellow
git status --short

# ==============================================================================
# 6. NETTOYAGE DES MODIFICATIONS NON DÉSIRÉES
# ==============================================================================
Write-Host "`n🧼 Étape 6/9: Nettoyage des modifications non désirées..." -ForegroundColor Yellow

# Ignorer les fichiers temporaires déjà trackés
git rm --cached -r . 2>$null
git add .

Write-Host "  ✅ Nettoyage effectué" -ForegroundColor Green

# ==============================================================================
# 7. VÉRIFICATION DES MODIFICATIONS
# ==============================================================================
Write-Host "`n📊 Étape 7/9: Analyse des modifications..." -ForegroundColor Yellow

$gitStatus = git status --porcelain
if ([string]::IsNullOrWhiteSpace($gitStatus)) {
    Write-Host "  ℹ️  Aucune modification à commiter" -ForegroundColor Cyan
    Write-Host "`n✅ Repository déjà à jour!" -ForegroundColor Green
    exit 0
}

# Afficher les modifications
Write-Host "  Modifications détectées:" -ForegroundColor White
git status --short | ForEach-Object {
    Write-Host "    $_" -ForegroundColor DarkGray
}

# ==============================================================================
# 8. COMMIT DES MODIFICATIONS
# ==============================================================================
Write-Host "`n💾 Étape 8/9: Commit des modifications..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$commitMessage = "fix(deploy): Configuration update $timestamp"

try {
    git add .
    git commit -m $commitMessage
    Write-Host "  ✅ Commit réussi: $commitMessage" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Erreur lors du commit: $_" -ForegroundColor Red
    exit 1
}

# ==============================================================================
# 9. PUSH VERS GITHUB
# ==============================================================================
Write-Host "`n⬆️  Étape 9/9: Push vers GitHub..." -ForegroundColor Yellow

try {
    # Vérifier la branche actuelle
    $currentBranch = git branch --show-current
    Write-Host "  Branche: $currentBranch" -ForegroundColor DarkGray
    
    # Push avec gestion d'erreur
    git push origin $currentBranch 2>&1 | ForEach-Object {
        if ($_ -match "error|fatal") {
            Write-Host "  ❌ $_" -ForegroundColor Red
        } elseif ($_ -match "warning") {
            Write-Host "  ⚠️  $_" -ForegroundColor Yellow
        } else {
            Write-Host "  $_" -ForegroundColor DarkGray
        }
    }
    
    Write-Host "  ✅ Push réussi vers origin/$currentBranch" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Erreur lors du push: $_" -ForegroundColor Red
    Write-Host "`n💡 Solutions possibles:" -ForegroundColor Cyan
    Write-Host "  1. Vérifiez votre connexion internet" -ForegroundColor White
    Write-Host "  2. Vérifiez vos credentials GitHub" -ForegroundColor White
    Write-Host "  3. Exécutez: git pull origin $currentBranch --rebase" -ForegroundColor White
    exit 1
}

# ==============================================================================
# 10. VÉRIFICATION FINALE
# ==============================================================================
Write-Host "`n✅ Vérification finale..." -ForegroundColor Yellow
git status
git log --oneline -3

Write-Host "`n" + "=" * 80 -ForegroundColor Gray
Write-Host "🎉 Déploiement terminé avec succès!" -ForegroundColor Green
Write-Host "`n📊 Résumé:" -ForegroundColor Cyan
Write-Host "  • Branche: $currentBranch" -ForegroundColor White
Write-Host "  • Dernier commit: $commitMessage" -ForegroundColor White
Write-Host "  • Streamlit Cloud: Auto-déploiement en cours (2-3 min)" -ForegroundColor White
Write-Host "=" * 80 -ForegroundColor Gray
