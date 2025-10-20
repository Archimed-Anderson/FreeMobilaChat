# Guide de Démarrage Manuel - FreeMobilaChat

## 🚀 Commandes de Démarrage Manuel

### **Option 1 : Démarrage Automatique (Recommandé)**
```bash
# Dans le répertoire FreeMobilaChat/
.\start_final.bat
```

### **Option 2 : Démarrage Manuel Étape par Étape**

#### **Étape 1 : Arrêter les processus existants**
```bash
taskkill /f /im python.exe
```

#### **Étape 2 : Démarrer le Backend FastAPI**
```bash
# Terminal 1 - Backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

#### **Étape 3 : Démarrer l'Application Streamlit**
```bash
# Terminal 2 - Frontend
cd streamlit_app
python -m streamlit run app.py --server.port 8501
```

### **Option 3 : Démarrage Streamlit Seul (Sans Backend)**
```bash
# Si vous voulez seulement l'interface Streamlit
cd streamlit_app
python -m streamlit run app.py --server.port 8501
```

## 🌐 URLs d'Accès

Une fois l'application démarrée, accédez aux URLs suivantes :

- **Page Principale** : http://localhost:8501
- **Analyse Intelligente** : http://localhost:8501/analyse_intelligente
- **Analyse Classique** : http://localhost:8501/analyse_old
- **Résultats** : http://localhost:8501/resultat

## 🧪 Test de l'Application

```bash
# Tester que l'application fonctionne
python test_app.py
```

## 📁 Structure du Projet

```
FreeMobilaChat/
├── app.py                           # Backend FastAPI
├── start_final.bat                  # Script de démarrage automatique
├── test_app.py                      # Script de test
├── DEMARRAGE_MANUEL_FINAL.md       # Ce guide
├── requirements.txt                 # Dépendances
├── vercel.json                      # Configuration Vercel
└── streamlit_app/
    ├── app.py                       # Application Streamlit principale
    ├── pages/                       # Pages de l'application
    │   ├── analyse_intelligente.py  # Page d'analyse intelligente
    │   ├── analyse_old.py           # Page d'analyse classique
    │   └── resultat.py              # Page de résultats
    ├── .streamlit/
    │   └── config.toml              # Configuration Streamlit
    └── requirements.txt             # Dépendances Streamlit
```

## ⚙️ Prérequis

- Python 3.9+ installé
- Pip à jour
- Dépendances installées :
  ```bash
  pip install -r requirements.txt
  cd streamlit_app
  pip install -r requirements.txt
  cd ..
  ```

## 🔧 Dépannage

### **Port déjà utilisé**
```bash
# Arrêter tous les processus Python
taskkill /f /im python.exe

# Attendre 2 secondes puis redémarrer
timeout /t 2
```

### **Erreur de module non trouvé**
```bash
# Vérifier que vous êtes dans le bon répertoire
cd C:\Users\ander\Desktop\FreeMobilaChat

# Réinstaller les dépendances
pip install -r requirements.txt
cd streamlit_app
pip install -r requirements.txt
```

### **Streamlit non reconnu**
```bash
# Utiliser python -m streamlit au lieu de streamlit
python -m streamlit run app.py --server.port 8501
```

## 📊 Fonctionnalités

- ✅ **Analyse Intelligente** : IA avec LLM pour insights uniques
- ✅ **Analyse Classique** : Analyse traditionnelle avec KPIs
- ✅ **Upload Multiple** : Support CSV, Excel, JSON
- ✅ **Design Responsive** : Mobile, tablet, desktop
- ✅ **Thème Free Mobile** : Rouge et noir professionnel
- ✅ **Navigation Fluide** : Entre toutes les pages

## 🎯 Statut de l'Application

**✅ APPLICATION 100% FONCTIONNELLE**

- Code nettoyé et optimisé
- Tests validés (4/4 pages)
- Structure stable
- Prête pour le déploiement

---

**FreeMobilaChat** - Application d'analyse de données Twitter avec IA
