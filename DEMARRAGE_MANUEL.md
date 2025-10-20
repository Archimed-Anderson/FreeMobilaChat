# Guide de Démarrage Manuel - FreeMobilaChat

## 🚀 Commandes de Démarrage

### **Option 1 : Script Automatique (Recommandé)**
```bash
# Démarrage complet avec un seul script
.\start_final.bat
```

### **Option 2 : Commandes Manuelles**

#### **Terminal 1 - Backend API**
```bash
# Démarrer le backend FastAPI
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

#### **Terminal 2 - Application Streamlit**
```bash
# Aller dans le dossier streamlit_app
cd streamlit_app

# Démarrer Streamlit
python -m streamlit run app.py --server.port 8501
```

## 🔧 Vérification du Démarrage

### **Test Rapide**
```bash
# Tester que l'application fonctionne
python test_app.py
```

### **URLs à Vérifier**
- **Page Principale** : http://localhost:8501
- **Analyse Intelligente** : http://localhost:8501/analyse_intelligente
- **Analyse Classique** : http://localhost:8501/analyse_old
- **Résultats** : http://localhost:8501/resultat

## 🛠️ Dépannage

### **Problème : Port déjà utilisé**
```bash
# Arrêter tous les processus Python
taskkill /f /im python.exe

# Attendre 2 secondes
timeout /t 2

# Redémarrer
.\start_final.bat
```

### **Problème : Application ne répond pas**
```bash
# Vérifier les ports
netstat -an | findstr :8501
netstat -an | findstr :8000

# Si aucun port en écoute, redémarrer
.\start_final.bat
```

### **Problème : Cache Streamlit**
```bash
# Nettoyer le cache Streamlit
streamlit cache clear

# Redémarrer l'application
.\start_final.bat
```

## 📋 Structure du Projet

```
FreeMobilaChat/
├── app.py                    # Backend FastAPI
├── start_final.bat          # Script de démarrage
├── test_app.py              # Test de validation
├── streamlit_app/
│   ├── app.py               # Application Streamlit principale
│   ├── pages/               # Pages de l'application
│   │   ├── analyse_intelligente.py
│   │   ├── analyse_old.py
│   │   └── resultat.py
│   └── .streamlit/
│       └── config.toml      # Configuration Streamlit
└── backend/                 # Code backend
```

## ⚡ Démarrage Rapide

1. **Ouvrir un terminal** dans le dossier `FreeMobilaChat`
2. **Exécuter** : `.\start_final.bat`
3. **Attendre** que les deux serveurs démarrent
4. **Ouvrir** : http://localhost:8501
5. **Tester** : `python test_app.py`

## 🎯 URLs de Production

- **Streamlit Cloud** : https://freemobilachat.streamlit.app
- **Vercel** : https://freemobilachat.vercel.app

## 📞 Support

En cas de problème :
1. Vérifier que Python est installé
2. Vérifier que les ports 8000 et 8501 sont libres
3. Exécuter `python test_app.py` pour diagnostiquer
4. Consulter les logs dans le terminal
