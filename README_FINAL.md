# FreeMobilaChat - Application d'Analyse IA

## 🚀 Démarrage Rapide

### **Démarrage Automatique**
```bash
# Cloner le projet
git clone https://github.com/Archimed-Anderson/FreeMobilaChat.git
cd FreeMobilaChat

# Démarrer l'application
.\start_final.bat
```

### **Démarrage Manuel**
```bash
# Terminal 1 - Backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd streamlit_app
python -m streamlit run app.py --server.port 8501
```

## 📱 Accès à l'Application

- **URL Locale** : http://localhost:8501
- **URL Production** : https://freemobilachat.streamlit.app

## 🧪 Test de l'Application

```bash
# Tester que l'application fonctionne
python test_app.py
```

## 📋 Pages Disponibles

- **Page Principale** : Interface d'accueil moderne
- **Analyse Intelligente** : Analyse IA avec LLM
- **Analyse Classique** : Analyse traditionnelle
- **Résultats** : Visualisations et rapports

## 🛠️ Structure du Projet

```
FreeMobilaChat/
├── app.py                           # Backend FastAPI
├── start_final.bat                 # Script de démarrage
├── test_app.py                     # Test de validation
├── DEMARRAGE_MANUEL.md             # Guide de démarrage
├── streamlit_app/
│   ├── app.py                      # Application Streamlit
│   ├── pages/                      # Pages de l'application
│   │   ├── analyse_intelligente.py
│   │   ├── analyse_old.py
│   │   └── resultat.py
│   └── .streamlit/
│       └── config.toml             # Configuration
└── backend/                        # Code backend
```

## 🔧 Prérequis

- Python 3.9+
- Streamlit
- FastAPI
- Uvicorn

## 📦 Installation des Dépendances

```bash
pip install -r requirements.txt
```

## 🎯 Fonctionnalités

- **Analyse Intelligente** : LLM pour insights uniques
- **Upload Multiple** : Support CSV, Excel, JSON
- **Visualisations** : Graphiques interactifs
- **Design Responsive** : Mobile, tablet, desktop
- **Thème Free Mobile** : Rouge et noir professionnel

## 🚀 Déploiement

### **Streamlit Cloud**
- Connecter le repository GitHub
- Déployer automatiquement

### **Vercel**
- Configuration `vercel.json` incluse
- Déploiement automatique

## 📞 Support

- **Documentation** : `DEMARRAGE_MANUEL.md`
- **Test** : `python test_app.py`
- **Logs** : Vérifier les terminaux de démarrage

## 🎉 Statut

✅ **Application Stable et Fonctionnelle**
✅ **Tests Automatisés**
✅ **Déploiement Production**
✅ **Documentation Complète**
