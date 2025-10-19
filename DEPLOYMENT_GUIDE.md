# Guide de Déploiement - FreeMobilaChat

## 🚀 Options de Déploiement

### Option 1 : Streamlit Cloud (Recommandé)

**Avantages** :
- Support natif de Streamlit
- Déploiement gratuit
- Intégration GitHub automatique
- Mise à jour automatique

**Étapes** :
1. Allez sur [https://share.streamlit.io/](https://share.streamlit.io/)
2. Connectez votre compte GitHub
3. Sélectionnez le repository : `Archimed-Anderson/FreeMobilaChat`
4. Définissez le chemin principal : `streamlit_app/app.py`
5. Cliquez sur "Deploy"

**URL de déploiement** : `https://freemobilachat.streamlit.app`

### Option 2 : Vercel (Avec FastAPI Wrapper)

**Avantages** :
- Performance élevée
- CDN global
- Déploiement automatique

**Configuration** :
- Fichier `app.py` : Wrapper FastAPI
- Fichier `vercel.json` : Configuration Vercel
- Fichier `requirements.txt` : Dépendances Python

**Étapes** :
1. Connectez votre repository GitHub à Vercel
2. Vercel détectera automatiquement la configuration
3. Déployez

### Option 3 : Heroku

**Avantages** :
- Support complet Python
- Facile à configurer
- Scaling automatique

**Fichiers requis** :
- `Procfile` : `web: streamlit run streamlit_app/app.py --server.port=$PORT --server.headless=true`
- `runtime.txt` : `python-3.11.0`

## 📁 Structure de Déploiement

```
FreeMobilaChat/
├── app.py                    # Wrapper FastAPI pour Vercel
├── vercel.json              # Configuration Vercel
├── requirements.txt         # Dépendances Python
├── .streamlit/
│   └── config.toml         # Configuration Streamlit
├── streamlit_app/          # Application principale
│   ├── app.py
│   ├── pages/
│   ├── components/
│   └── ...
└── DEPLOYMENT_GUIDE.md     # Ce guide
```

## 🔧 Configuration des Variables d'Environnement

### Variables Requises

```bash
# API Keys (optionnelles pour les fonctionnalités avancées)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Configuration Streamlit
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Configuration Vercel

Dans le dashboard Vercel, ajoutez ces variables :
- `PYTHONPATH` = `streamlit_app`
- `STREAMLIT_SERVER_HEADLESS` = `true`

## 🐛 Résolution des Problèmes

### Erreur Vercel : "No FastAPI entrypoint found"

**Solution** : Utilisez le fichier `app.py` fourni qui contient un wrapper FastAPI.

### Erreur Streamlit : "Module not found"

**Solution** : Vérifiez que `requirements.txt` contient toutes les dépendances.

### Erreur de Port

**Solution** : Utilisez la variable d'environnement `PORT` pour Heroku ou port 8501 pour Streamlit Cloud.

## 📊 Monitoring et Logs

### Streamlit Cloud
- Logs disponibles dans le dashboard
- Métriques d'utilisation
- Gestion des erreurs

### Vercel
- Logs dans le dashboard Vercel
- Analytics de performance
- Monitoring des erreurs

## 🔄 Mise à Jour

### Déploiement Automatique
- **Streamlit Cloud** : Mise à jour automatique à chaque push
- **Vercel** : Redéploiement automatique
- **Heroku** : Redéploiement manuel ou via GitHub

### Déploiement Manuel
```bash
# Streamlit Cloud
git push origin main

# Vercel
vercel --prod

# Heroku
git push heroku main
```

## 🎯 Recommandations

1. **Pour la démonstration** : Utilisez Streamlit Cloud
2. **Pour la production** : Utilisez Vercel avec le wrapper FastAPI
3. **Pour le développement** : Utilisez Heroku

## 📞 Support

En cas de problème :
1. Vérifiez les logs de déploiement
2. Consultez la documentation de la plateforme
3. Vérifiez la configuration des variables d'environnement