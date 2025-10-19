# FreeMobilaChat - Application d'Analyse de Données Twitter

<div align="center">

![FreeMobilaChat Logo](https://img.shields.io/badge/FreeMobilaChat-Data%20Analysis-CC0000?style=for-the-badge&logo=python&logoColor=white)

**Application d'analyse avancée de données Twitter avec intelligence artificielle**

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-Academic-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=flat-square)](https://github.com/Archimed-Anderson/FreeMobilaChat)

</div>

---

## 📋 Table des Matières

- [Description du Projet](#-description-du-projet)
- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Architecture Technique](#-architecture-technique)
- [Structure du Projet](#-structure-du-projet)
- [Installation et Utilisation](#-installation-et-utilisation)
- [Déploiement](#-déploiement)
- [Technologies Utilisées](#-technologies-utilisées)
- [Documentation](#-documentation)
- [Contribution](#-contribution)
- [Auteur](#-auteur)

---

## 🎯 Description du Projet

FreeMobilaChat est une application web développée dans le cadre d'un **mémoire de master en Data Science**. Cette application permet l'analyse avancée de données Twitter en utilisant l'intelligence artificielle pour :

- **Classification automatique** des tweets par catégories
- **Analyse de sentiment** en temps réel
- **Génération d'indicateurs de performance (KPIs)** personnalisés
- **Visualisations interactives** des données analysées

L'application offre une interface utilisateur moderne et intuitive, permettant aux utilisateurs d'uploader leurs données Twitter et d'obtenir des insights actionnables grâce à des algorithmes d'IA avancés.

---

## ⭐ Fonctionnalités Principales

### 🖥️ Interface Utilisateur Moderne
- **Design responsive** avec thème Free Mobile personnalisé
- **Navigation intuitive** entre les différentes sections
- **Interface d'upload** de fichiers drag & drop
- **Visualisations interactives** avec Plotly

### 📊 Analyse de Données Avancée
- **Support multi-formats** : CSV, Excel, JSON, Parquet
- **Analyse de sentiment** automatique avec scores de confiance
- **Classification par catégories** intelligente
- **Calcul de priorités** basé sur l'IA
- **Génération de KPIs** en temps réel

### 📈 Visualisations Interactives
- **Graphiques dynamiques** avec Plotly Express
- **Tableaux de bord** personnalisables
- **Export des résultats** en différents formats
- **Filtres avancés** pour l'exploration des données

---

## 🏗️ Architecture Technique

### Frontend (Streamlit)
```
streamlit_app/
├── app.py                 # Point d'entrée principal
├── pages/                 # Pages de l'application
│   ├── 01_analyse.py      # Page d'upload et d'analyse
│   └── 02_resultat.py     # Page de visualisation des résultats
├── components/            # Composants réutilisables
│   ├── upload_handler.py  # Gestionnaire d'upload
│   ├── analysis_engine.py # Moteur d'analyse
│   └── ui_components.py   # Composants UI
├── config/               # Configuration de l'application
│   ├── settings.py       # Paramètres généraux
│   └── api_config.py     # Configuration API
├── services/             # Services métier
│   ├── data_processor.py # Traitement des données
│   ├── kpi_calculator.py # Calcul des KPIs
│   └── file_analyzer.py  # Analyse des fichiers
└── utils/                # Fonctions utilitaires
    ├── helpers.py        # Fonctions d'aide
    └── validators.py     # Validation des données
```

### Backend (FastAPI)
```
backend/
├── app/                  # Application FastAPI
│   ├── main.py          # Point d'entrée API
│   ├── models.py        # Modèles de données
│   ├── schemas.py       # Schémas Pydantic
│   ├── services/        # Services backend
│   │   ├── llm_service.py      # Service LLM
│   │   ├── analysis_service.py # Service d'analyse
│   │   └── database_service.py # Service base de données
│   └── utils/           # Utilitaires backend
├── data/                # Données et modèles
│   ├── processed/       # Données traitées
│   ├── raw/            # Données brutes
│   └── results/        # Résultats d'analyse
├── tests/              # Tests unitaires
└── requirements.txt    # Dépendances backend
```

### Infrastructure
```
├── docker-compose.yml      # Configuration Docker
├── nginx.conf             # Configuration Nginx
├── docs/                  # Documentation technique
│   ├── deployment/        # Guides de déploiement
│   ├── setup-guides/      # Guides d'installation
│   └── operational-procedures/ # Procédures opérationnelles
└── visualizations/        # Visualisations générées
```

---

## 🚀 Installation et Utilisation

### Prérequis
- **Python 3.9+**
- **pip** (gestionnaire de paquets Python)
- **Git** (pour cloner le repository)

### Installation Rapide

1. **Cloner le repository**
```bash
   git clone https://github.com/Archimed-Anderson/FreeMobilaChat.git
   cd FreeMobilaChat/streamlit_app
   ```

2. **Installer les dépendances**
```bash
   pip install -r requirements.txt
```

3. **Lancer l'application**
```bash
   streamlit run app.py
   ```

4. **Accéder à l'application**
   ```
   http://localhost:8501
   ```

### Installation Complète (avec Backend)

1. **Cloner le repository complet**
   ```bash
   git clone https://github.com/Archimed-Anderson/FreeMobilaChat.git
   cd FreeMobilaChat
   ```

2. **Installer les dépendances frontend**
```bash
   cd streamlit_app
   pip install -r requirements.txt
   ```

3. **Installer les dépendances backend**
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. **Lancer le backend**
```bash
   python start_server.py
   ```

5. **Lancer le frontend**
```bash
   cd ../streamlit_app
   streamlit run app.py
   ```

---

## 🌐 Déploiement

### Déploiement Local
L'application peut être déployée localement en suivant les instructions d'installation ci-dessus.

### Déploiement sur Streamlit Cloud
1. Aller sur [share.streamlit.io](https://share.streamlit.io)
2. Connecter votre compte GitHub
3. Sélectionner le repository `FreeMobilaChat`
4. Configurer :
   - **Main file path** : `streamlit_app/app.py`
   - **Python version** : 3.9
   - **Requirements file** : `streamlit_app/requirements.txt`

### Déploiement avec Docker
```bash
docker-compose up -d
```

---

## 🛠️ Technologies Utilisées

### Frontend
- **[Streamlit](https://streamlit.io)** - Framework web pour applications de données
- **[Plotly](https://plotly.com)** - Bibliothèque de visualisation interactive
- **[Pandas](https://pandas.pydata.org)** - Manipulation et analyse de données
- **[NumPy](https://numpy.org)** - Calculs numériques
- **[Font Awesome](https://fontawesome.com)** - Icônes modernes

### Backend
- **[FastAPI](https://fastapi.tiangolo.com)** - Framework web moderne et rapide
- **[SQLite](https://sqlite.org)** - Base de données relationnelle
- **[Pydantic](https://pydantic-docs.helpmanual.io)** - Validation de données
- **[Ollama](https://ollama.ai)** - Intégration LLM locale

### Infrastructure
- **[Docker](https://docker.com)** - Conteneurisation
- **[Nginx](https://nginx.org)** - Serveur web et proxy
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD

---

## 📚 Documentation

### Documentation Technique
- [Guide de Déploiement](streamlit_app/DEPLOYMENT.md)
- [Guide d'Installation](docs/setup-guides/)
- [Procédures Opérationnelles](docs/operational-procedures/)

### Documentation Académique
- [Rapport Bloc CC2.1](Rapport_Bloc_CC2.1_FreeMobilaChat_2025-10-18/)
- [Visualisations](visualizations/)

---

## 🤝 Contribution

Ce projet a été développé dans le cadre d'un mémoire de master en Data Science. Pour toute question ou suggestion :

1. Créer une [issue](https://github.com/Archimed-Anderson/FreeMobilaChat/issues)
2. Proposer une [pull request](https://github.com/Archimed-Anderson/FreeMobilaChat/pulls)

---

## 👨‍💻 Auteur

**Archimed Anderson**  
*Étudiant en Master Data Science*

- **Repository** : [GitHub](https://github.com/Archimed-Anderson/FreeMobilaChat)
- **Projet** : Mémoire de master en Data Science
- **Année** : 2025

---

## 📄 Licence

Ce projet est développé dans le cadre académique d'un mémoire de master.  
**Usage éducatif uniquement.**

---

<div align="center">

**FreeMobilaChat** - *Transformez vos données Twitter en insights actionnables*

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/Archimed-Anderson/FreeMobilaChat)
[![Streamlit](https://img.shields.io/badge/Streamlit-Demo-red?style=for-the-badge&logo=streamlit)](https://share.streamlit.io)

</div>