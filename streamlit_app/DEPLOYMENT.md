# Guide de Déploiement - FreeMobilaChat

## Déploiement Local

### Prérequis
- Python 3.9 ou supérieur
- pip installé

### Installation
1. Cloner le repository :
   ```bash
   git clone https://github.com/Archimed-Anderson/FreeMobilaChat.git
   cd FreeMobilaChat/streamlit_app
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancer l'application :
   ```bash
   streamlit run app.py
   ```

L'application sera accessible à l'adresse : `http://localhost:8501`

## Déploiement sur Streamlit Cloud

### Configuration automatique
Le projet est configuré pour un déploiement automatique sur Streamlit Cloud via GitHub Actions.

### Configuration manuelle
1. Aller sur [share.streamlit.io](https://share.streamlit.io)
2. Connecter votre compte GitHub
3. Sélectionner le repository `FreeMobilaChat`
4. Configurer :
   - **Main file path** : `streamlit_app/app.py`
   - **Python version** : 3.9
   - **Requirements file** : `streamlit_app/requirements.txt`

## Variables d'Environnement

Aucune variable d'environnement n'est requise pour le fonctionnement de base de l'application.

## Structure de Déploiement

```
streamlit_app/
├── app.py                 # Point d'entrée principal
├── pages/                 # Pages de l'application
├── components/            # Composants réutilisables
├── config/               # Configuration
├── services/             # Services métier
├── utils/                # Fonctions utilitaires
├── requirements.txt      # Dépendances Python
├── .streamlit/           # Configuration Streamlit
└── .github/workflows/    # CI/CD GitHub Actions
```

## Monitoring et Logs

- Les logs sont stockés dans le dossier `logs/`
- L'application génère des logs d'erreur et d'information
- Monitoring disponible via l'interface Streamlit Cloud

## Support

Pour toute question concernant le déploiement, consulter la documentation Streamlit ou créer une issue sur GitHub.
