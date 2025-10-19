# FreeMobilaChat - Application Streamlit Moderne

## 🚀 Vue d'ensemble

FreeMobilaChat est une application Streamlit moderne et robuste pour l'analyse avancée de données Twitter avec intelligence artificielle. L'application offre une interface utilisateur professionnelle, une architecture modulaire et une gestion robuste des erreurs.

## ✨ Fonctionnalités Principales

### 🔍 Analyse Avancée
- **Upload multi-formats** : CSV, Excel, JSON, Parquet
- **Validation robuste** : Détection d'encodage, validation des données
- **Analyse en temps réel** : Sentiment, catégorisation, priorité
- **KPIs interactifs** : Métriques personnalisées par rôle utilisateur

### 🎨 Interface Moderne
- **Design responsive** : Mobile-friendly avec breakpoints CSS
- **Thème professionnel** : Palette de couleurs cohérente
- **Animations fluides** : Transitions et effets visuels
- **Dark mode** : Support automatique du mode sombre

### 🏗️ Architecture Robuste
- **Gestion d'erreurs** : Fallbacks et retry automatique
- **Configuration centralisée** : Paramètres par environnement
- **API client robuste** : Connexions multiples avec fallback
- **Session management** : Gestion d'état optimisée

## 📁 Structure du Projet

```
streamlit_app/
├── 📁 app.py                    # Point d'entrée principal
├── 📁 config/
│   ├── settings.py              # Configuration centralisée
│   └── api_config.py            # Gestion connexions API
├── 📁 pages/
│   ├── 01_analyse.py            # Page principale d'analyse
│   ├── 02_dashboard.py          # Dashboard avec visualisations
│   ├── 03_settings.py           # Configuration utilisateur
│   └── 04_about.py              # Documentation
├── 📁 components/
│   ├── upload_handler.py        # Gestionnaire upload robuste
│   ├── analysis_engine.py       # Moteur d'analyse KPI
│   ├── ui_components.py         # Composants UI modernes
│   └── error_handler.py         # Gestion erreurs centralisée
├── 📁 services/
│   ├── data_processor.py        # Traitement données
│   └── kpi_calculator.py        # Calcul indicateurs
├── 📁 assets/
│   └── styles.css               # CSS moderne
├── 📁 utils/
│   ├── validators.py            # Validation données
│   └── helpers.py               # Fonctions utilitaires
└── 📁 requirements.txt          # Dépendances Python
```

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.9+
- pip ou conda

### Installation
```bash
# Cloner le repository
git clone https://github.com/freemobilachat/streamlit-app.git
cd streamlit-app

# Installer les dépendances
pip install -r requirements.txt

# Démarrer l'application
streamlit run app.py
```

### Configuration
1. **Variables d'environnement** (optionnel) :
   ```bash
   export STREAMLIT_ENV=production
   export API_TIMEOUT=60
   export MAX_FILE_SIZE=52428800
   ```

2. **Configuration API** :
   - Modifiez `config/api_config.py` pour vos URLs d'API
   - Ajoutez vos clés API dans `config/settings.py`

## 🎯 Utilisation

### 1. Page d'Analyse (Principale)
- **Upload de fichiers** : Glissez-déposez vos données
- **Configuration** : Choisissez vos paramètres d'analyse
- **Lancement** : Démarrez l'analyse en un clic
- **Redirection automatique** : Vers le dashboard

### 2. Dashboard KPI
- **Métriques principales** : Vue d'ensemble des KPIs
- **Visualisations interactives** : Graphiques Plotly
- **Filtres avancés** : Par sentiment, catégorie, priorité
- **Export** : PDF, Excel, JSON

### 3. Configuration
- **Rôles utilisateur** : Manager, Analyst, Agent, Admin
- **Paramètres IA** : Fournisseur, température, batch size
- **Thème** : Mode sombre/clair

## 🔧 Configuration Avancée

### Rôles Utilisateur
```python
# KPIs par rôle
ROLE_KPIS = {
    UserRole.MANAGER: ["total_tweets", "sentiment_distribution", "cost_analysis"],
    UserRole.ANALYST: ["sentiment_analysis", "trend_analysis", "correlation_analysis"],
    UserRole.AGENT: ["urgent_tweets", "response_needed", "sentiment_alerts"],
    UserRole.ADMIN: ["system_health", "performance_metrics", "error_logs"]
}
```

### API Configuration
```python
# URLs de fallback
API_CONFIGS = {
    "backend": [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://0.0.0.0:8000"
    ]
}
```

### Thème Personnalisé
```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --accent-color: #f093fb;
    /* ... autres variables */
}
```

## 🛠️ Développement

### Structure Modulaire
- **config/** : Configuration centralisée
- **components/** : Composants réutilisables
- **services/** : Logique métier
- **utils/** : Fonctions utilitaires
- **pages/** : Pages Streamlit

### Ajout de Nouveaux KPIs
```python
# Dans services/kpi_calculator.py
def calculate_custom_kpi(self, data: pd.DataFrame) -> Dict[str, Any]:
    return {
        "custom_metric": value,
        "custom_score": score
    }
```

### Ajout de Nouveaux Composants UI
```python
# Dans components/ui_components.py
def render_custom_component(data: Dict[str, Any]):
    st.markdown("### Custom Component")
    # Votre logique ici
```

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/

# Tests avec couverture
pytest --cov=streamlit_app tests/

# Tests d'intégration
pytest tests/integration/
```

## 📊 Performance

### Optimisations
- **Cache Streamlit** : `@st.cache_data` sur les fonctions lourdes
- **Lazy loading** : Chargement à la demande
- **Chunking** : Traitement par lots
- **Session state** : Gestion optimisée

### Métriques
- **Temps de chargement** : < 3 secondes
- **Mémoire** : < 500MB pour 10k tweets
- **Responsive** : Breakpoints mobile/tablet/desktop

## 🚨 Gestion d'Erreurs

### Types d'Erreurs
- **Connexion API** : Fallback automatique
- **Validation données** : Messages détaillés
- **Upload fichiers** : Gestion des formats
- **Analyse** : Retry avec backoff

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Message d'information")
logger.error("Message d'erreur")
```

## 🔒 Sécurité

### Validation
- **Types de fichiers** : Formats autorisés uniquement
- **Taille maximale** : Limite configurable
- **Sanitization** : Nettoyage des données
- **Session** : Gestion sécurisée

### Audit
- **Logs d'upload** : Traçabilité complète
- **Métriques d'usage** : Analytics intégrées
- **Error tracking** : Stack traces détaillées

## 📈 Monitoring

### Health Checks
- **API status** : Vérification automatique
- **Métriques temps réel** : Performance live
- **Error tracking** : Surveillance des erreurs
- **Usage analytics** : Statistiques d'utilisation

## 🚀 Déploiement

### Production
```bash
# Variables d'environnement
export STREAMLIT_ENV=production
export API_BASE_URL=https://api.freemobilachat.com

# Démarrage
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 🤝 Contribution

### Guidelines
1. **Code style** : Black + flake8
2. **Tests** : Couverture > 80%
3. **Documentation** : Docstrings complètes
4. **Commits** : Messages descriptifs

### Workflow
1. Fork du repository
2. Création d'une branche feature
3. Développement avec tests
4. Pull request avec description

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.

## 🆘 Support

### Documentation
- **Guide utilisateur** : [docs/user-guide.md](docs/user-guide.md)
- **API reference** : [docs/api-reference.md](docs/api-reference.md)
- **FAQ** : [docs/faq.md](docs/faq.md)

### Contact
- **Issues** : [GitHub Issues](https://github.com/freemobilachat/issues)
- **Email** : support@freemobilachat.com
- **Discord** : [Discord Server](https://discord.gg/freemobilachat)

## 🎉 Remerciements

- **Streamlit** : Framework de base
- **Plotly** : Visualisations interactives
- **Pandas** : Traitement des données
- **Communauté** : Contributions et feedback

---

**FreeMobilaChat** - Analyse avancée de données Twitter avec IA 🚀
