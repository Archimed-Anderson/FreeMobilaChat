# Commandes Manuelles - FreeMobilaChat (Version Finale)

## 🚀 Démarrage Rapide

### Option 1 : Script Automatique (Recommandé)
```bash
# Double-cliquez sur start_manual.bat
# OU
# Exécutez dans PowerShell
.\start_manual.bat
```

### Option 2 : Commandes Manuelles (2 terminaux)

#### Terminal 1 - Backend API
```bash
# Dans le répertoire racine FreeMobilaChat
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Application Streamlit
```bash
# Dans le répertoire FreeMobilaChat
cd streamlit_app
python -m streamlit run app.py --server.port 8501
```

## 📍 URLs Disponibles

- **Application Principale** : http://localhost:8501
- **Analyse Intelligente** : http://localhost:8501/analyse_intelligente
- **Analyse Classique** : http://localhost:8501/analyse_old
- **Résultats** : http://localhost:8501/resultat
- **Backend API** : http://localhost:8000

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

### Problème : "Page not found"
**Solution** : Vérifiez que le fichier `.streamlit/config.toml` existe
```bash
# Vérifier la structure
ls streamlit_app/.streamlit/
ls streamlit_app/pages/
```

### Problème : "streamlit n'est pas reconnu"
**Solution** : Utilisez `python -m streamlit` au lieu de `streamlit`

### Problème : Port déjà utilisé
**Solution** : Changez le port
```bash
python -m streamlit run app.py --server.port 8502
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
5. **Configuration** : Le fichier `.streamlit/config.toml` est essentiel

## 🎯 Structure des Fichiers

```
FreeMobilaChat/
├── app.py                          # Backend FastAPI
├── start_manual.bat                # Script de démarrage
├── streamlit_app/
│   ├── app.py                      # Application Streamlit principale
│   ├── .streamlit/
│   │   └── config.toml            # Configuration Streamlit
│   └── pages/
│       ├── 01_analyse_intelligente.py
│       ├── 02_analyse_old.py
│       └── 03_resultat.py
└── requirements.txt
```

## 🚨 Problèmes Résolus

- ✅ **Configuration Streamlit** : Fichier `.streamlit/config.toml` recréé
- ✅ **Pages reconnues** : Structure des pages corrigée
- ✅ **Navigation** : URLs directes fonctionnelles
- ✅ **Cache** : Nettoyage complet effectué
