# 🚀 Guide de Déploiement FreeMobilaChat

## ⚠️ Problèmes Courants Git sur Windows et Solutions

### 🔴 Erreur: "LF will be replaced by CRLF"
**Cause**: Différence entre les fins de ligne Windows (CRLF) et Linux (LF)

**Solution appliquée**:
```powershell
git config --local core.autocrlf true
git config --local core.safecrlf warn
```

### 🔴 Erreur: "fatal: not a git repository"
**Solution**:
```powershell
cd c:\Users\ander\Desktop\FreeMobilaChat
```

### 🔴 Erreur: "Permission denied" ou "Authentication failed"
**Solutions**:
1. Vérifiez vos credentials GitHub
2. Utilisez Personal Access Token au lieu du mot de passe
3. Configurez SSH keys

## 📁 Scripts de Déploiement Disponibles

### 1️⃣ PowerShell (Recommandé pour Windows)
```powershell
# Déploiement complet avec vérifications
.\deploy-windows.ps1

# Déploiement rapide
.\quick-deploy.ps1
```

### 2️⃣ Git Bash
```bash
# Rendre le script exécutable
chmod +x deploy-windows.sh

# Exécuter
./deploy-windows.sh
```

## 🎯 Utilisation Rapide

### Option A: Quick Deploy (1 commande)
```powershell
.\quick-deploy.ps1
```

### Option B: Quick Deploy avec message personnalisé
```powershell
.\quick-deploy.ps1 -Message "feat: Nouvelle fonctionnalité"
```

### Option C: Déploiement complet avec toutes les vérifications
```powershell
.\deploy-windows.ps1
```

## 🛠️ Commandes Git Manuelles (si scripts échouent)

### Workflow Standard
```powershell
# 1. Nettoyage
git config --local core.autocrlf true
git status

# 2. Ajout des modifications
git add .

# 3. Commit
git commit -m "fix: Description de la modification"

# 4. Push
git push origin main
```

### En cas de conflit
```powershell
# Récupérer les dernières modifications
git pull origin main --rebase

# Résoudre les conflits manuellement, puis:
git add .
git rebase --continue
git push origin main
```

### Reset en cas de problème
```powershell
# Annuler le dernier commit (garde les modifications)
git reset --soft HEAD~1

# Annuler toutes les modifications locales
git reset --hard origin/main
```

## 📊 Vérifications Post-Déploiement

1. **GitHub**: Vérifiez que le commit apparaît sur https://github.com/Anderson-Archimede/FreeMobilaChat

2. **Streamlit Cloud**: 
   - Auto-déploiement démarre automatiquement (2-3 minutes)
   - URL: https://freemobilachat-rw6fofuxokw4stxcvubwoc.streamlit.app/

3. **Logs de déploiement**:
   - Visible dans Streamlit Cloud dashboard
   - Vérifiez les erreurs de build

## 🔍 Debugging

### Vérifier l'état du repository
```powershell
git status
git log --oneline -5
git remote -v
```

### Vérifier les fichiers ignorés
```powershell
git ls-files --others --ignored --exclude-standard
```

### Forcer le push (⚠️ Utiliser avec précaution)
```powershell
git push origin main --force
```

## 📝 Structure des Commits

Utilisez les préfixes suivants:
- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `docs:` - Documentation
- `style:` - Formatage
- `refactor:` - Refactoring
- `test:` - Tests
- `chore:` - Maintenance

**Exemples**:
```
feat: Add new classification algorithm
fix: Resolve DOM removeChild error
docs: Update deployment guide
```

## 🆘 Support

Si les scripts échouent:
1. Vérifiez que vous êtes dans le bon répertoire
2. Vérifiez votre connexion internet
3. Vérifiez vos credentials GitHub
4. Consultez les logs d'erreur complets
5. Essayez le déploiement manuel avec les commandes Git
