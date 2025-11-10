#!/bin/bash
# ==============================================================================
# 🚀 Script de Déploiement FreeMobilaChat - Git Bash (Windows)
# ==============================================================================
# Version: 1.0
# Auteur: AI DevOps Engineer
# Compatible: Git Bash on Windows
# ==============================================================================

set -e  # Exit on error

echo "🚀 Déploiement FreeMobilaChat - Démarrage"
echo "================================================================================"

# ==============================================================================
# 1. NETTOYAGE DES FICHIERS TEMPORAIRES
# ==============================================================================
echo ""
echo "🧹 Étape 1/9: Nettoyage des fichiers temporaires..."

# Supprimer __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Supprimer *.pyc
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Supprimer .DS_Store
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

echo "  ✅ Nettoyage terminé"

# ==============================================================================
# 2. CONFIGURATION STREAMLIT
# ==============================================================================
echo ""
echo "⚙️  Étape 2/9: Configuration de Streamlit..."

# Créer les répertoires
mkdir -p .streamlit
mkdir -p streamlit_app/.streamlit

# Créer le fichier de configuration
cat > .streamlit/config.toml << 'EOF'
[server]
port = 8501
headless = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
base = "light"
primaryColor = "#1E3A5F"
EOF

# Copier la configuration
cp .streamlit/config.toml streamlit_app/.streamlit/config.toml

echo "  ✅ Configuration Streamlit créée"

# ==============================================================================
# 3. CONFIGURATION GIT
# ==============================================================================
echo ""
echo "🔄 Étape 3/9: Configuration Git..."

# Configuration Git pour Windows
git config --local core.autocrlf true
git config --local core.safecrlf warn
git config --local core.filemode false

echo "  ✅ Git configuré"

# ==============================================================================
# 4. VÉRIFICATION DES FICHIERS ESSENTIELS
# ==============================================================================
echo ""
echo "📝 Étape 4/9: Vérification des fichiers essentiels..."

ALL_FILES_EXIST=true

check_file() {
    if [ -f "$1" ]; then
        echo "  ✓ $1"
    else
        echo "  ✗ MANQUANT: $1"
        ALL_FILES_EXIST=false
    fi
}

check_file "requirements-academic.txt"
check_file "README.md"
check_file ".gitignore"
check_file "streamlit_app/Home.py"

if [ "$ALL_FILES_EXIST" = true ]; then
    echo "  ✅ Tous les fichiers essentiels présents"
else
    echo "  ⚠️  Certains fichiers manquent"
fi

# ==============================================================================
# 5. STATUS GIT ACTUEL
# ==============================================================================
echo ""
echo "🔍 Étape 5/9: Status Git actuel..."
git status --short

# ==============================================================================
# 6. NETTOYAGE DES MODIFICATIONS NON DÉSIRÉES
# ==============================================================================
echo ""
echo "🧼 Étape 6/9: Nettoyage des modifications non désirées..."

# Retirer du cache les fichiers temporaires
git rm --cached -r . 2>/dev/null || true
git add .

echo "  ✅ Nettoyage effectué"

# ==============================================================================
# 7. VÉRIFICATION DES MODIFICATIONS
# ==============================================================================
echo ""
echo "📊 Étape 7/9: Analyse des modifications..."

if [ -z "$(git status --porcelain)" ]; then
    echo "  ℹ️  Aucune modification à commiter"
    echo ""
    echo "✅ Repository déjà à jour!"
    exit 0
fi

echo "  Modifications détectées:"
git status --short | sed 's/^/    /'

# ==============================================================================
# 8. COMMIT DES MODIFICATIONS
# ==============================================================================
echo ""
echo "💾 Étape 8/9: Commit des modifications..."

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
COMMIT_MESSAGE="fix(deploy): Configuration update $TIMESTAMP"

git add .
git commit -m "$COMMIT_MESSAGE"

echo "  ✅ Commit réussi: $COMMIT_MESSAGE"

# ==============================================================================
# 9. PUSH VERS GITHUB
# ==============================================================================
echo ""
echo "⬆️  Étape 9/9: Push vers GitHub..."

CURRENT_BRANCH=$(git branch --show-current)
echo "  Branche: $CURRENT_BRANCH"

if git push origin "$CURRENT_BRANCH" 2>&1; then
    echo "  ✅ Push réussi vers origin/$CURRENT_BRANCH"
else
    echo "  ❌ Erreur lors du push"
    echo ""
    echo "💡 Solutions possibles:"
    echo "  1. Vérifiez votre connexion internet"
    echo "  2. Vérifiez vos credentials GitHub"
    echo "  3. Exécutez: git pull origin $CURRENT_BRANCH --rebase"
    exit 1
fi

# ==============================================================================
# 10. VÉRIFICATION FINALE
# ==============================================================================
echo ""
echo "✅ Vérification finale..."
git status
echo ""
git log --oneline -3

echo ""
echo "================================================================================"
echo "🎉 Déploiement terminé avec succès!"
echo ""
echo "📊 Résumé:"
echo "  • Branche: $CURRENT_BRANCH"
echo "  • Dernier commit: $COMMIT_MESSAGE"
echo "  • Streamlit Cloud: Auto-déploiement en cours (2-3 min)"
echo "================================================================================"
