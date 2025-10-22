# Module de Classification LLM - Guide Rapide

## 🚀 Démarrage Rapide

### Installation

```bash
pip install -r requirements.txt
```

### Usage Basique

```python
from app.services.tweet_classifier import classify_tweet

# Classification simple
result = classify_tweet("@Free Ma box ne marche plus !")
print(f"Réclamation: {result.is_reclamation}")
print(f"Thème: {result.theme}")
print(f"Urgence: {result.urgence}")
```

### Entraînement

```bash
python train_classifier.py \
    --data ../data/raw/free_tweet_export.csv \
    --model gpt-4 \
    --n-samples 500
```

### Tests

```bash
python tests/test_tweet_classifier.py
```

## 📊 Taxonomie

- **is_reclamation**: OUI | NON
- **theme**: FIBRE | MOBILE | TV | FACTURE | SAV | RESEAU | AUTRE
- **sentiment**: NEGATIF | NEUTRE | POSITIF
- **urgence**: FAIBLE | MOYENNE | ELEVEE | CRITIQUE
- **type_incident**: PANNE | LENTEUR | FACTURATION | PROCESSUS_SAV | INFO | AUTRE

## 📖 Documentation Complète

Voir [DOCUMENTATION_CLASSIFICATION_LLM.md](../DOCUMENTATION_CLASSIFICATION_LLM.md)

## 🤝 Contribution

1. Créer une branche: `git checkout -b feature/ma-feature`
2. Commiter: `git commit -am 'Ajout feature'`
3. Push: `git push origin feature/ma-feature`
4. Créer une Pull Request

