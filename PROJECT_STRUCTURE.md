# Structure Détaillée du Projet FreeMobilaChat

## Vue d'Ensemble

```
FreeMobilaChat/
├── 📁 streamlit_app/           # Application Frontend (Streamlit)
├── 📁 backend/                 # Services Backend (FastAPI)
├── 📁 docs/                    # Documentation Technique
├── 📁 data/                    # Données et Datasets
├── 📁 visualizations/          # Visualisations Générées
├── 📁 Rapport_Bloc_CC2.1_*/   # Documentation Académique
├── 📄 README.md               # Documentation Principale
├── 📄 PROJECT_STRUCTURE.md    # Ce fichier
└── 📄 docker-compose.yml      # Configuration Docker
```

---

## 🎯 Frontend (Streamlit Application)

### Structure Principale
```
streamlit_app/
├── 📄 app.py                  # Point d'entrée principal
├── 📄 requirements.txt        # Dépendances Python
├── 📄 run.py                  # Script de lancement
├── 📄 run_production.py       # Script de production
├── 📄 deploy_production.py    # Script de déploiement
├── 📄 DEPLOYMENT.md           # Guide de déploiement
├── 📄 .gitignore              # Fichiers à ignorer
├── 📄 .streamlit/             # Configuration Streamlit
│   └── 📄 config.toml         # Configuration thème
└── 📁 .github/workflows/      # CI/CD GitHub Actions
    └── 📄 deploy.yml          # Workflow de déploiement
```

### Pages de l'Application
```
streamlit_app/pages/
├── 📄 01_analyse.py           # Page d'upload et d'analyse
└── 📄 02_resultat.py          # Page de visualisation des résultats
```

### Composants Réutilisables
```
streamlit_app/components/
├── 📄 upload_handler.py       # Gestionnaire d'upload de fichiers
├── 📄 analysis_engine.py      # Moteur d'analyse des données
└── 📄 ui_components.py        # Composants UI réutilisables
```

### Configuration
```
streamlit_app/config/
├── 📄 settings.py             # Paramètres généraux de l'application
└── 📄 api_config.py           # Configuration des APIs externes
```

### Services Métier
```
streamlit_app/services/
├── 📄 data_processor.py       # Traitement et transformation des données
├── 📄 kpi_calculator.py       # Calcul des indicateurs de performance
└── 📄 file_analyzer.py        # Analyse des fichiers uploadés
```

### Utilitaires
```
streamlit_app/utils/
├── 📄 helpers.py              # Fonctions d'aide générales
└── 📄 validators.py           # Validation des données et fichiers
```

### Assets
```
streamlit_app/assets/
├── 📄 styles.css              # Styles CSS personnalisés
└── 📄 logo.py                 # Génération du logo SVG
```

---

## 🔧 Backend (FastAPI Services)

### Structure Principale
```
backend/
├── 📄 main.py                 # Point d'entrée FastAPI
├── 📄 requirements.txt        # Dépendances backend
├── 📄 start_server.py         # Script de démarrage serveur
├── 📄 start_production.py     # Script de production
├── 📄 Dockerfile              # Configuration Docker
└── 📄 audit_summary.md        # Résumé d'audit
```

### Application FastAPI
```
backend/app/
├── 📄 main.py                 # Configuration FastAPI principale
├── 📄 models.py               # Modèles de données SQLAlchemy
├── 📄 schemas.py              # Schémas Pydantic
├── 📄 config.py               # Configuration backend
├── 📄 exceptions.py           # Gestion des exceptions
├── 📁 services/               # Services métier backend
│   ├── 📄 llm_service.py      # Service d'intégration LLM
│   ├── 📄 analysis_service.py # Service d'analyse des données
│   ├── 📄 database_service.py # Service de base de données
│   └── 📄 ...                 # Autres services
├── 📁 utils/                  # Utilitaires backend
│   └── 📄 ...                 # Fonctions utilitaires
└── 📁 config_pkg/             # Configuration avancée
    └── 📄 ...                 # Fichiers de configuration
```

### Données et Modèles
```
backend/data/
├── 📁 processed/              # Données traitées
├── 📁 raw/                    # Données brutes
├── 📁 results/                # Résultats d'analyse
│   └── 📄 *.json              # Fichiers de résultats
├── 📁 training/               # Données d'entraînement
│   ├── 📄 *.csv               # Datasets CSV
│   └── 📄 *.json              # Métadonnées
└── 📄 freemobilachat.db       # Base de données SQLite
```

### Tests
```
backend/tests/
├── 📄 test_*.py               # Tests unitaires
└── 📄 ...                     # Tests d'intégration
```

---

## 📚 Documentation

### Documentation Technique
```
docs/
├── 📄 README.md               # Documentation générale
├── 📄 FAST_GRAPHRAG_INTEGRATION.md
├── 📁 deployment/             # Guides de déploiement
│   ├── 📄 DEPLOYMENT.md
│   ├── 📄 GPU_TRAINING_GUIDE.md
│   ├── 📄 MANAGER_PRESENTATION_SUMMARY.md
│   └── 📄 PRODUCTION_DEPLOYMENT_GUIDE.md
├── 📁 setup-guides/           # Guides d'installation
│   ├── 📄 API_KEYS_PRODUCTION_SETUP.md
│   ├── 📄 DOMAIN_DNS_SETUP.md
│   ├── 📄 SMTP_ALERTS_SETUP.md
│   └── 📄 SSL_SETUP_GUIDE.md
└── 📁 operational-procedures/ # Procédures opérationnelles
    └── 📄 BACKUP_SYSTEM_GUIDE.md
```

### Documentation Académique
```
Rapport_Bloc_CC2.1_FreeMobilaChat_2025-10-18/
├── 📄 Rapport_Bloc_CC2.1_FreeMobilaChat.md
├── 📄 Resume_Executif_CC2.1.md
├── 📄 LIVRABLES_CC2.1.md
├── 📄 README_Rapport_CC2.1.md
├── 📄 dataset_statistics.json
├── 📄 generate_visualizations.py
├── 📁 visualizations/         # Graphiques générés
│   ├── 📄 1_distribution_sentiments.png
│   ├── 📄 2_distribution_categories.png
│   ├── 📄 3_distribution_priorites.png
│   ├── 📄 4_correlation_sentiment_categorie.png
│   ├── 📄 5_distribution_longueur_textes.png
│   ├── 📄 6_evolution_temporelle.png
│   ├── 📄 7_nuages_mots_sentiments.png
│   └── 📄 8_kpi_operationnels.png
└── 📄 *.csv                   # Datasets d'exemple
```

---

## 🗄️ Données et Ressources

### Datasets
```
data/
├── 📁 fast_graphrag/          # Données FastGraphRAG
├── 📁 fast_graphrag_test/     # Tests FastGraphRAG
├── 📁 processed/              # Données traitées
├── 📁 raw/                    # Données brutes
│   ├── 📄 free_tweet_export.csv
│   └── 📄 free tweet export.xlsx
├── 📁 samples/                # Échantillons de données
│   └── 📄 sample_tweets.csv
├── 📁 training/               # Données d'entraînement
│   ├── 📄 dataset_statistics.json
│   ├── 📄 test_dataset.csv
│   ├── 📄 train_dataset.csv
│   └── 📄 validation_dataset.csv
└── 📄 README.md               # Documentation des données
```

### Visualisations
```
visualizations/
├── 📄 1_distribution_sentiments.png
├── 📄 2_distribution_categories.png
├── 📄 3_distribution_priorites.png
├── 📄 4_correlation_sentiment_categorie.png
├── 📄 5_distribution_longueur_textes.png
├── 📄 6_evolution_temporelle.png
├── 📄 7_nuages_mots_sentiments.png
└── 📄 8_kpi_operationnels.png
```

---

## 🐳 Infrastructure et Déploiement

### Configuration Docker
```
├── 📄 docker-compose.yml      # Configuration Docker Compose
├── 📄 docker-compose.scalable.yml  # Configuration scalable
├── 📄 nginx.conf              # Configuration Nginx
├── 📄 nginx.scalable.conf     # Configuration Nginx scalable
└── 📁 ssl/                    # Certificats SSL
```

### Scripts de Base de Données
```
├── 📄 init-db.sql             # Initialisation base de données
├── 📄 create_chatbot_tables.sql
└── 📄 recreate_chatbot_tables.sql
```

### Logs et Monitoring
```
├── 📁 logs/                   # Fichiers de logs
├── 📁 backups/                # Sauvegardes
│   ├── 📁 daily/              # Sauvegardes quotidiennes
│   ├── 📁 weekly/             # Sauvegardes hebdomadaires
│   ├── 📁 monthly/            # Sauvegardes mensuelles
│   └── 📁 logs/               # Logs de sauvegarde
└── 📁 uploads/                # Fichiers uploadés
```

---

## 📊 Statistiques du Projet

- **Total des fichiers** : 100+ fichiers
- **Lignes de code** : 15,000+ lignes
- **Technologies** : Python, Streamlit, FastAPI, SQLite, Docker
- **Documentation** : 20+ fichiers de documentation
- **Tests** : 20+ fichiers de tests
- **Visualisations** : 8 graphiques générés

---

## 🚀 Points d'Entrée

### Développement
```bash
# Frontend uniquement
cd streamlit_app
streamlit run app.py

# Backend uniquement
cd backend
python start_server.py

# Full stack
docker-compose up
```

### Production
```bash
# Déploiement complet
cd streamlit_app
python deploy_production.py

# Monitoring
./monitor_production.sh
```

---

*Cette structure reflète l'architecture complète du projet FreeMobilaChat, développé dans le cadre d'un mémoire de master en Data Science.*