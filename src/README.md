# 🏗️ FreeMobilaChat Backend - Nouvelle Architecture

## 📋 Vue d'ensemble

Architecture restructurée du backend avec modules NLP et LLM séparés, tests complets et gestion d'erreurs avancée.

## 📁 Structure

```
src/
├── core/                           # Modules principaux
│   ├── NLP_processing/            # Traitement NLP
│   │   ├── sentiment_analysis.py  # Analyse de sentiment
│   │   └── text_cleaning.py       # Nettoyage de texte
│   └── LLM_integration/           # Intégration LLM
│       ├── api_client.py          # Client API unifié
│       └── response_handler.py    # Gestion des réponses
├── utils/                         # Utilitaires
│   ├── file_handlers/
│   │   └── read_file.py          # Lecture fichiers CSV
│   └── logging/
│       └── error_handler.py      # Gestion d'erreurs
└── requirements.txt               # Dépendances

storage/
└── datasets/
    └── dataset.csv                # Données principales

tests/
├── units/                         # Tests unitaires
│   ├── file_handlers/
│   └── nlp_processing/
└── integration/                   # Tests d'intégration
    └── llm_pipeline/
```

## 🚀 Installation

### 1. Installer les dépendances

```bash
# Dépendances principales
pip install -r src/requirements.txt

# Dépendances de test
pip install -r requirements-test.txt
```

### 2. Configuration

Les modules utilisent des variables d'environnement pour les API keys :

```bash
# OpenAI
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4o-mini"

# Mistral
export MISTRAL_API_KEY="your-key"
export MISTRAL_MODEL="mistral-small-latest"

# Anthropic
export ANTHROPIC_API_KEY="your-key"
export ANTHROPIC_MODEL="claude-3-haiku-20240307"

# Ollama (local)
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.1:8b"
```

## 💻 Utilisation

### 1. Lecture de fichiers CSV

```python
from src.utils.file_handlers.read_file import readCSV, readTweetsCSV

# Lecture basique
df = readCSV("storage/datasets/dataset.csv")

# Lecture avec validation colonnes tweets
df = readTweetsCSV("storage/datasets/dataset.csv")
```

### 2. Nettoyage de texte

```python
from src.core.NLP_processing.text_cleaning import TextCleaner

cleaner = TextCleaner()

# Nettoyage pour analyse
text = "@Free le réseau est nul 😡 https://t.co/xxx"
cleaned = cleaner.clean_for_analysis(text)

# Extraction d'éléments
mentions = cleaner.extract_mentions(text)
hashtags = cleaner.extract_hashtags(text)
urls = cleaner.extract_urls(text)

# Détection de cas spéciaux
info = cleaner.handle_special_cases(text)
print(info['is_too_short'], info['has_irony_markers'])
```

### 3. Analyse de sentiment

```python
from src.core.NLP_processing.sentiment_analysis import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyse simple
result = analyzer.analyze_sentiment("Le service est excellent!")
print(result['sentiment'])  # 'positive'
print(result['score'])      # 0.8
print(result['confidence']) # 0.9

# Analyse avec contexte (détection ironie)
result = analyzer.analyze_with_context("Super service lol", consider_irony=True)

# Analyse batch
texts = ["Tweet 1", "Tweet 2", "Tweet 3"]
results = analyzer.batch_analyze(texts)

# Distribution des sentiments
distribution = analyzer.get_sentiment_distribution(texts)
```

### 4. Client API LLM

```python
from src.core.LLM_integration.api_client import LLMAPIClient
import asyncio

# Initialiser le client
client = LLMAPIClient(
    provider="openai",  # ou "mistral", "anthropic", "ollama"
    timeout=5.0,
    max_retries=3
)

# Appel asynchrone
async def analyze():
    result = await client.call_api(
        prompt="Analyse ce tweet: Service excellent",
        system_prompt="Tu es un analyseur de sentiment",
        temperature=0.3,
        max_tokens=300
    )
    return result

result = asyncio.run(analyze())

# Statistiques
stats = client.get_stats()
print(f"Calls: {stats['successful_calls']}/{stats['total_calls']}")
print(f"Avg duration: {stats['average_duration']:.2f}s")
```

### 5. Gestion des réponses LLM

```python
from src.core.LLM_integration.response_handler import ResponseHandler

handler = ResponseHandler()

# Parser une réponse
raw_response = '''```json
{
    "sentiment": "positive",
    "sentiment_score": 0.8,
    "category": "compliment",
    "priority": "basse",
    "keywords": ["excellent"],
    "is_urgent": false,
    "needs_response": false,
    "estimated_resolution_time": null
}
```'''

result = handler.process_response(raw_response)

# Valider la réponse
try:
    handler.validate_response(result)
    print("Réponse valide!")
except ResponseValidationError as e:
    print(f"Erreur: {e}")

# Traiter un batch
responses = [response1, response2, response3]
results = handler.batch_process_responses(responses)
```

### 6. Gestion d'erreurs et logging

```python
from src.utils.logging.error_handler import ErrorHandler, handle_errors

# Initialiser le gestionnaire
error_handler = ErrorHandler(log_dir="logs", log_level=logging.INFO)

# Logger une erreur
try:
    # Code qui peut échouer
    pass
except Exception as e:
    error_handler.log_error(
        error=e,
        context={'param': 'value'},
        module_name='mon_module'
    )

# Logger des performances
error_handler.log_performance(
    operation="data_processing",
    duration=2.5,
    metadata={'rows': 1000}
)

# Obtenir les statistiques
stats = error_handler.get_error_stats()

# Exporter un rapport
error_handler.export_error_report("error_report.json")

# Utiliser le décorateur
@handle_errors(module_name="my_module")
def my_function():
    # Code here
    pass
```

## 🔄 Workflow complet

```python
from src.utils.file_handlers.read_file import readTweetsCSV
from src.core.NLP_processing.text_cleaning import TextCleaner
from src.core.NLP_processing.sentiment_analysis import SentimentAnalyzer
from src.core.LLM_integration.api_client import LLMAPIClient
from src.core.LLM_integration.response_handler import ResponseHandler
from src.utils.logging.error_handler import ErrorHandler
import asyncio

async def process_tweets():
    # 1. Charger les données
    df = readTweetsCSV("storage/datasets/dataset.csv")
    
    # 2. Nettoyer les textes
    cleaner = TextCleaner()
    df['cleaned_text'] = df['text'].apply(cleaner.clean_for_analysis)
    
    # 3. Analyse de sentiment locale (rapide)
    analyzer = SentimentAnalyzer()
    df['local_sentiment'] = df['cleaned_text'].apply(
        lambda x: analyzer.analyze_sentiment(x)['sentiment']
    )
    
    # 4. Analyse LLM pour les cas complexes
    llm_client = LLMAPIClient(provider="openai")
    response_handler = ResponseHandler()
    
    llm_results = []
    for text in df['cleaned_text'].head(10):  # Exemple sur 10 tweets
        result = await llm_client.call_api(
            prompt=f"Analyse: {text}",
            system_prompt="Analyse de sentiment tweet SAV"
        )
        parsed = response_handler.process_response(result['content'])
        llm_results.append(parsed)
    
    # 5. Logger les résultats
    error_handler = ErrorHandler()
    stats = llm_client.get_stats()
    error_handler.log_performance(
        operation="llm_analysis",
        duration=stats['total_duration'],
        metadata={'tweets': 10}
    )
    
    return df, llm_results

# Exécuter
df, results = asyncio.run(process_tweets())
```

## 🧪 Tests

Voir [README_TESTS.md](../README_TESTS.md) pour la documentation complète des tests.

```bash
# Tous les tests
pytest

# Tests unitaires
pytest tests/units/ -v

# Tests d'intégration
pytest tests/integration/ -v

# Avec couverture
pytest --cov=src --cov-report=html
```

## 📊 Caractéristiques

### NLP Processing

- ✅ Nettoyage robuste (emojis, mentions, URLs)
- ✅ Gestion Unicode et caractères spéciaux
- ✅ Détection spam et ironie
- ✅ Analyse sentiment multiclasse
- ✅ Extraction mots-clés
- ✅ Support tweets 10-280 caractères

### LLM Integration

- ✅ Multi-providers (OpenAI, Mistral, Anthropic, Ollama)
- ✅ Timeout configurable (défaut 5s)
- ✅ Retry automatique avec backoff exponentiel
- ✅ Gestion réponses vides
- ✅ Tracking statistiques
- ✅ Rate limiting

### Gestion d'erreurs

- ✅ Logging centralisé
- ✅ Tracking erreurs par type/module
- ✅ Métriques de performance
- ✅ Export rapports JSON
- ✅ Décorateurs pour automatisation

## 🔧 Configuration avancée

### Timeout LLM personnalisé

```python
client = LLMAPIClient(
    provider="openai",
    timeout=10.0,  # 10 secondes
    max_retries=5
)
```

### Logging personnalisé

```python
error_handler = ErrorHandler(
    log_dir="custom_logs",
    log_level=logging.DEBUG,
    enable_console=True
)
```

### Nettoyage de texte personnalisé

```python
cleaner = TextCleaner()
text = cleaner.clean_for_analysis(
    text,
    preserve_mentions=False,  # Supprimer @mentions
    preserve_hashtags=True,   # Garder #hashtags
    preserve_emojis=False     # Supprimer emojis
)
```

## 📈 Performance

- **Lecture CSV** : < 5s pour 10,000 tweets
- **Nettoyage texte** : ~0.001s par tweet
- **Analyse sentiment** : ~0.0001s par tweet
- **Appel LLM** : 0.5-3s selon provider (avec timeout 5s)
- **Pipeline complet** : < 5s pour 100 tweets (sans LLM)

## 🐛 Debugging

### Activer les logs verbeux

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Tester la connexion LLM

```python
client = LLMAPIClient(provider="openai")
is_connected = await client.test_connection()
print(f"Connected: {is_connected}")
```

## 📚 Dépendances

- **pandas** >= 2.0.0 : Manipulation de données
- **httpx** >= 0.26.0 : Client HTTP async

## 🔒 Sécurité

- ⚠️ Ne jamais commit les API keys
- ✅ Utiliser des variables d'environnement
- ✅ Valider toutes les entrées utilisateur
- ✅ Gérer les timeouts pour éviter les blocages

## 🤝 Contribution

1. Les modules existants **ne doivent pas être modifiés**
2. Maintenir la compatibilité des signatures de fonctions
3. Ajouter des tests pour toute nouvelle fonctionnalité
4. Documenter les nouvelles API

## 📝 Changelog

### Version 2.0.0 (Novembre 2024)

- ✨ Nouvelle architecture modulaire
- ✨ Support multi-providers LLM
- ✨ Tests complets (unitaires + intégration)
- ✨ Gestion d'erreurs avancée
- ✨ Documentation complète

## 📧 Support

Pour toute question ou problème, consulter :
- [README_TESTS.md](../README_TESTS.md) pour les tests
- Les docstrings dans chaque module
- Les exemples d'utilisation ci-dessus

---

**Version** : 2.0.0  
**License** : MIT  
**Auteur** : FreeMobilaChat Team

