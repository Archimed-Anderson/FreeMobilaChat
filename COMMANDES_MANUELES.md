# Commandes Manuelles - FreeMobilaChat

## 🚀 Démarrage Rapide

### Option 1 : Script Automatique (Recommandé)
```bash
# Double-cliquez sur start_app.bat
# OU
# Exécutez dans PowerShell
.\start_app.ps1
```

### Option 2 : Commandes Manuelles

#### 1. Démarrer le Backend API
```bash
# Terminal 1 - Backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

#### 2. Démarrer l'Application Streamlit
```bash
# Terminal 2 - Frontend
cd streamlit_app
streamlit run app.py --server.port 8501
```

## 📍 URLs Disponibles

- **Backend API** : http://localhost:8000
- **Application Streamlit** : http://localhost:8501
- **Page Principale** : http://localhost:8501/
- **Analyse Intelligente** : http://localhost:8501/analyse_intelligente
- **Analyse Classique** : http://localhost:8501/analyse_old
- **Résultats** : http://localhost:8501/resultat

## 🔧 Configuration PATH (Une seule fois)

### Méthode 1 : Interface Graphique
1. `Windows + R` → `sysdm.cpl` → Entrée
2. "Variables d'environnement" → "Variables système"
3. Trouvez "Path" → "Modifier" → "Nouveau"
4. Ajoutez : `C:\Users\ander\AppData\Roaming\Python\Python312\Scripts`
5. "OK" sur toutes les fenêtres
6. Redémarrez votre terminal

### Méthode 2 : PowerShell (Temporaire)
```powershell
$env:PATH += ";C:\Users\ander\AppData\Roaming\Python\Python312\Scripts"
```

## ✅ Vérification

```bash
# Vérifier que Streamlit est accessible
streamlit --version

# Vérifier que les ports sont libres
netstat -an | findstr :8000
netstat -an | findstr :8501
```

## 🛠️ Dépannage

### Problème : "streamlit n'est pas reconnu"
**Solution** : Utilisez `python -m streamlit` au lieu de `streamlit`

### Problème : Port déjà utilisé
**Solution** : Changez le port
```bash
streamlit run app.py --server.port 8502
```

### Problème : Module non trouvé
**Solution** : Installez les dépendances
```bash
pip install -r requirements.txt
```

## 📝 Notes Importantes

1. **Ordre de démarrage** : Toujours démarrer le backend avant Streamlit
2. **Ports** : 8000 (Backend) et 8501 (Streamlit) par défaut
3. **Terminal** : Gardez les deux terminaux ouverts pendant l'utilisation
4. **Arrêt** : Ctrl+C dans chaque terminal pour arrêter les services
