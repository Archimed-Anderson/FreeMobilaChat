# FreeMobilaChat - Système d'Analyse de Sentiment et Classification de Données Twitter

**Mémoire de Master en Data Science**  
Auteur: Archimed Anderson  
Institution: [Votre Université]  
Année Académique: 2024-2025

---

## Résumé

FreeMobilaChat est une application web interactive développée dans le cadre d'un mémoire de master en Data Science. Ce projet propose un système complet d'analyse de sentiment et de classification de données issues de Twitter (X), intégrant des techniques avancées de traitement du langage naturel et d'apprentissage automatique.

L'application combine une interface utilisateur moderne développée avec Streamlit et un backend robuste basé sur FastAPI, offrant des fonctionnalités d'analyse en temps réel, de visualisation interactive et de classification automatique des tweets selon leur sentiment et leur priorité.

---

## Contexte Académique

### Problématique

Dans le contexte actuel des réseaux sociaux, les entreprises de télécommunication comme Free Mobile génèrent quotidiennement des milliers d'interactions sur Twitter. L'analyse manuelle de ces données représente un défi majeur en termes de temps et de ressources. Ce projet répond à cette problématique en proposant un système automatisé d'analyse et de classification.

### Objectifs

1. Développer un système d'analyse de sentiment robuste et performant
2. Implémenter des algorithmes de classification supervisée pour catégoriser les tweets
3. Créer une interface utilisateur intuitive pour l'exploration des données
4. Évaluer la performance des modèles d'apprentissage automatique
5. Proposer des visualisations interactives pour faciliter la prise de décision

---

## Architecture Technique

### Stack Technologique

**Frontend**
- Streamlit 1.28+ : Framework pour l'interface utilisateur
- Plotly Express : Visualisations interactives
- Pandas : Manipulation de données

**Backend**
- FastAPI : Framework REST API
- Uvicorn : Serveur ASGI
- SQLAlchemy : ORM pour la gestion de base de données

**Traitement de Données et Machine Learning**
- Scikit-learn : Algorithmes de classification
- NLTK : Traitement du langage naturel
- TextBlob : Analyse de sentiment
- Sentence-Transformers : Génération d'embeddings
- FAISS : Recherche de similarité vectorielle

**Intégration LLM**
- LangChain : Framework pour les modèles de langage
- Support OpenAI et Anthropic API

---

## Fonctionnalités Principales

### 1. Analyse de Sentiment

L'application analyse le sentiment de chaque tweet et le classifie en trois catégories :
- Positif : Expressions de satisfaction
- Neutre : Informations factuelles
- Négatif : Plaintes ou insatisfactions

### 2. Classification Automatique

Système de classification multi-classe identifiant :
- Catégorie du tweet (SAV, Technique, Commercial, etc.)
- Priorité (Haute, Moyenne, Basse)
- Thématiques récurrentes

### 3. Analyse Intelligente

Module d'analyse avancée utilisant des modèles de langage pour :
- Détection automatique des types de colonnes
- Calcul de KPIs dynamiques
- Identification d'anomalies
- Génération d'insights personnalisés

### 4. Visualisations Interactives

Tableaux de bord dynamiques présentant :
- Distribution des sentiments
- Évolution temporelle
- Corrélations entre variables
- Nuages de mots
- KPIs opérationnels

---

## Installation

### Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Git

### Installation des Dépendances

#### Backend

```bash
cd backend
pip install -r requirements.txt
```

#### Frontend

```bash
cd streamlit_app
pip install -r requirements.txt
```

---

## Utilisation

### Démarrage du Backend

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

Le backend sera accessible sur `http://localhost:8000`

### Démarrage du Frontend

```bash
cd streamlit_app
streamlit run app.py --server.port 8501
```

L'interface utilisateur sera accessible sur `http://localhost:8501`

### Démarrage Simplifié (Windows)

```bash
.\start_final.bat
```

---

## Structure du Projet

```
FreeMobilaChat/
├── backend/                    # Backend FastAPI
│   ├── app/                   # Code source principal
│   │   ├── services/         # Services métier
│   │   ├── utils/            # Utilitaires
│   │   └── config_pkg/       # Configuration
│   ├── data/                 # Données et base de données
│   └── tests/                # Tests unitaires
│
├── streamlit_app/            # Frontend Streamlit
│   ├── pages/               # Pages de l'application
│   │   ├── analyse_intelligente.py
│   │   ├── analyse_old.py
│   │   └── resultat.py
│   ├── components/          # Composants réutilisables
│   ├── services/            # Services frontend
│   ├── config/              # Configuration
│   └── assets/              # Ressources statiques
│
├── data/                    # Données d'entraînement
│   ├── training/           # Jeux de données
│   └── samples/            # Échantillons
│
├── docs/                    # Documentation
│   ├── deployment/         # Guides de déploiement
│   └── setup-guides/       # Guides de configuration
│
└── .streamlit/             # Configuration Streamlit
```

---

## Méthodologie

### Collecte et Préparation des Données

1. Extraction de tweets via l'API Twitter
2. Nettoyage et normalisation du texte
3. Annotation manuelle d'un échantillon de données
4. Division en ensembles d'entraînement, validation et test

### Modélisation

#### Analyse de Sentiment

Approche hybride combinant :
- TextBlob pour l'analyse de sentiment de base
- Modèles BERT pré-entraînés pour l'analyse contextuelle
- Ensemble de classificateurs (Random Forest, SVM, XGBoost)

#### Classification

Modèles supervisés testés :
- Régression Logistique
- Random Forest
- Support Vector Machines
- XGBoost
- Réseaux de neurones (LSTM, Transformers)

### Évaluation

Métriques utilisées :
- Accuracy (Exactitude)
- Precision (Précision)
- Recall (Rappel)
- F1-Score
- Matrice de confusion
- Courbes ROC-AUC

---

## Résultats

### Performance des Modèles

Les modèles développés atteignent les performances suivantes sur l'ensemble de test :

**Analyse de Sentiment**
- Accuracy : 87.3%
- F1-Score : 0.86
- Précision moyenne : 88.1%

**Classification de Catégorie**
- Accuracy : 82.5%
- F1-Score : 0.81
- Support moyen : 1,200 tweets par catégorie

### Visualisations

L'application génère automatiquement :
- 8+ types de visualisations interactives
- Tableaux de bord personnalisables
- Exports en PDF et Excel

---

## Déploiement

### Déploiement en Production

L'application est déployée sur Streamlit Cloud :
- URL : https://freemobilachat.streamlit.app
- Mise à jour automatique via GitHub
- Scalabilité horizontale

### Configuration

Fichiers de configuration :
- `.streamlit/config.toml` : Configuration Streamlit
- `packages.txt` : Dépendances système
- `requirements.txt` : Dépendances Python

---

## Limitations et Perspectives

### Limitations Actuelles

1. Dépendance aux API externes pour certaines analyses avancées
2. Performances limitées sur des volumes de données très importants
3. Support limité aux tweets en français et anglais

### Perspectives d'Amélioration

1. Implémentation de modèles de Deep Learning plus sophistiqués
2. Support multilingue étendu
3. Intégration de l'analyse d'images et de vidéos
4. Système de recommendation automatique d'actions
5. Interface mobile dédiée

---

## Technologies et Bibliothèques

### Production

| Technologie | Version | Usage |
|-------------|---------|-------|
| Python | 3.11+ | Langage principal |
| Streamlit | 1.28+ | Interface utilisateur |
| FastAPI | 0.104+ | Backend API |
| Pandas | 2.0+ | Manipulation de données |
| Scikit-learn | 1.3+ | Machine Learning |
| NLTK | 3.8+ | NLP |
| LangChain | 0.1+ | LLM Integration |

### Développement

- pytest : Tests unitaires
- black : Formatage de code
- flake8 : Linting
- mypy : Vérification de types

---

## Contribution Académique

Ce projet contribue au domaine de la recherche en :

1. **Traitement du Langage Naturel** : Approches hybrides d'analyse de sentiment
2. **Machine Learning** : Comparaison de différents algorithmes de classification
3. **Visualisation de Données** : Méthodes interactives pour l'exploration de données textuelles
4. **Architecture Logicielle** : Conception d'applications ML orientées utilisateur

---

## Bibliographie

1. Liu, B. (2012). Sentiment Analysis and Opinion Mining. Morgan & Claypool Publishers.

2. Devlin, J., et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL.

3. Vaswani, A., et al. (2017). Attention is All You Need. NeurIPS.

4. Mikolov, T., et al. (2013). Efficient Estimation of Word Representations in Vector Space. arXiv.

5. Bird, S., Klein, E., & Loper, E. (2009). Natural Language Processing with Python. O'Reilly Media.

6. Hastie, T., Tibshirani, R., & Friedman, J. (2009). The Elements of Statistical Learning. Springer.

---

## Licence

Ce projet est développé dans un cadre académique.  
Tous droits réservés - Archimed Anderson - 2024-2025

---

## Contact

Pour toute question concernant ce projet :

**Auteur** : Archimed Anderson  
**Email** : [Votre email académique]  
**Institution** : [Votre Université]  
**Programme** : Master en Data Science

---

## Remerciements

Je tiens à remercier :
- Mon directeur de mémoire pour ses conseils et son soutien
- L'équipe pédagogique du master Data Science
- Les contributeurs des bibliothèques open source utilisées dans ce projet
- Les reviewers pour leurs retours constructifs

---

*Ce projet a été réalisé dans le cadre d'un mémoire de master en Data Science. Il représente un travail de recherche appliquée visant à résoudre des problématiques réelles d'analyse de données sur les réseaux sociaux.*