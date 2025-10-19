# Guide d'Intégration FreeMobilaChat

## 🚀 Démarrage Rapide

### 1. Installation des Dépendances

```bash
# Installation automatique
python run.py --install-deps

# Ou installation manuelle
pip install -r requirements.txt
```

### 2. Vérification de la Configuration

```bash
# Vérification complète
python run.py --check-config

# Vérification des modules
python -c "import streamlit, pandas, plotly; print('✅ Modules OK')"
```

### 3. Démarrage de l'Application

```bash
# Mode développement
python run.py --env development

# Mode production
python run.py --env production --port 8501

# Mode debug
python run.py --env development --debug
```

## 🔧 Configuration

### Variables d'Environnement

```bash
# Environnement
export STREAMLIT_ENV=production

# API
export API_BASE_URL=http://localhost:8000
export API_TIMEOUT=60

# Fichiers
export MAX_FILE_SIZE=52428800  # 50MB

# Logging
export STREAMLIT_LOGGER_LEVEL=info
```

### Configuration API

Modifiez `config/api_config.py` :

```python
API_CONFIGS = {
    "backend": [
        "http://127.0.0.1:8000",      # URL principale
        "http://localhost:8000",       # Fallback 1
        "http://0.0.0.0:8000"         # Fallback 2
    ]
}
```

## 🧪 Tests

### Tests d'Intégration

```bash
# Tous les tests
python test_integration.py

# Tests spécifiques
python -m unittest TestConfiguration
python -m unittest TestAPIClient
python -m unittest TestUploadHandler
```

### Tests de Performance

```bash
# Test de charge
python -c "
import time
import pandas as pd
from streamlit_app.services.kpi_calculator import get_kpi_calculator

# Création de données de test
data = pd.DataFrame({
    'text': ['Test tweet'] * 1000,
    'author': ['user'] * 1000,
    'retweet_count': [5] * 1000
})

# Test de performance
start = time.time()
kpi_calculator = get_kpi_calculator()
kpis = kpi_calculator.calculate_kpis(data, {})
end = time.time()

print(f'Temps d\'exécution: {end - start:.2f}s')
print(f'KPIs calculés: {len(kpis)}')
"
```

## 🐛 Débogage

### Logs

```bash
# Niveau de log
export STREAMLIT_LOGGER_LEVEL=debug

# Fichier de log
streamlit run app.py --logger.level debug 2>&1 | tee app.log
```

### Problèmes Courants

#### 1. Erreur de Connexion API

```
HTTPConnectionPool(host='127.0.0.1', port=8000): Read timed out
```

**Solution :**
```bash
# Vérifier que le serveur backend est démarré
curl http://localhost:8000/health

# Ou démarrer le serveur
python backend/start_server.py
```

#### 2. Module Non Trouvé

```
ModuleNotFoundError: No module named 'streamlit_app'
```

**Solution :**
```bash
# Vérifier le PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou utiliser le script run.py
python run.py
```

#### 3. Erreur de Permissions

```
PermissionError: [Errno 13] Permission denied
```

**Solution :**
```bash
# Vérifier les permissions
ls -la streamlit_app/

# Corriger les permissions
chmod +x run.py
chmod +x test_integration.py
```

## 📊 Monitoring

### Métriques de Performance

```python
# Dans votre code
import time
import logging

logger = logging.getLogger(__name__)

def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} executed in {end - start:.2f}s")
        return result
    return wrapper

@monitor_performance
def calculate_kpis(data, config):
    # Votre code ici
    pass
```

### Health Checks

```bash
# Vérification de l'API
curl -f http://localhost:8000/health || echo "API non disponible"

# Vérification de Streamlit
curl -f http://localhost:8501 || echo "Streamlit non disponible"
```

## 🚀 Déploiement

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["python", "run.py", "--env", "production"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_ENV=production
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
  
  backend:
    image: freemobilachat/backend:latest
    ports:
      - "8000:8000"
```

### Production

```bash
# Variables d'environnement
export STREAMLIT_ENV=production
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true

# Démarrage
streamlit run app.py
```

## 🔒 Sécurité

### Validation des Données

```python
# Validation stricte
from streamlit_app.utils.validators import FileValidator

validator = FileValidator()
result = validator.validate_file(uploaded_file)

if not result["valid"]:
    st.error(f"Erreur: {result['error']}")
    return
```

### Gestion des Erreurs

```python
# Gestion robuste des erreurs
try:
    result = api_client.make_request("GET", "/endpoint")
    if result and result.status_code == 200:
        data = result.json()
    else:
        st.error("Erreur de connexion API")
except Exception as e:
    logger.error(f"Erreur inattendue: {e}")
    st.error("Erreur technique")
```

## 📈 Optimisation

### Cache Streamlit

```python
@st.cache_data
def expensive_function(data):
    # Fonction coûteuse
    return processed_data
```

### Lazy Loading

```python
# Chargement à la demande
if st.button("Charger les données"):
    data = load_data()
    st.dataframe(data)
```

### Chunking

```python
# Traitement par lots
def process_large_dataset(data, chunk_size=1000):
    for chunk in pd.read_csv(data, chunksize=chunk_size):
        yield process_chunk(chunk)
```

## 🆘 Support

### Logs de Débogage

```bash
# Logs détaillés
python run.py --debug 2>&1 | tee debug.log

# Analyse des logs
grep "ERROR" debug.log
grep "WARNING" debug.log
```

### Rapport de Bug

```bash
# Informations système
python -c "
import sys
import platform
print(f'Python: {sys.version}')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Architecture: {platform.machine()}')
"

# Modules installés
pip list | grep -E "(streamlit|pandas|plotly)"
```

### Contact

- **Issues** : [GitHub Issues](https://github.com/freemobilachat/issues)
- **Email** : support@freemobilachat.com
- **Discord** : [Discord Server](https://discord.gg/freemobilachat)

---

**FreeMobilaChat** - Guide d'intégration complet 🚀
