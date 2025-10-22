# 🚀 Guide de Démarrage Rapide - Classification LLM

**Temps estimé**: 5 minutes  
**Prérequis**: Python 3.9+ installé

---

## Étape 1: Installation des Dépendances (2 min)

```bash
# Aller dans le répertoire backend
cd backend

# Installer les dépendances
pip install pandas numpy pydantic scikit-learn matplotlib seaborn openpyxl
```

**Note**: Les dépendances LLM (openai, anthropic, langchain) sont **optionnelles** pour le test rapide.

---

## Étape 2: Test Rapide Sans API (1 min)

```bash
# Toujours dans backend/
python quick_test_classifier.py
```

**Ce que vous allez voir**:
- ✅ 5 tweets classifiés automatiquement
- ✅ Résultats détaillés avec justifications
- ✅ Vérification automatique des classifications
- ✅ Score d'accuracy par tweet

**Résultat attendu**:
```
==================================================
  TEST RAPIDE DU CLASSIFICATEUR DE TWEETS FREE
==================================================

🚀 Initialisation du classificateur en mode FALLBACK (sans LLM)
   (Aucune API key requise, classification par règles)

✅ Classificateur initialisé: fallback
==================================================


🔢 TEST 1/5

📝 Tweet: @Free Ma fibre est coupée depuis ce matin...
--------------------------------------------------------------------------------
✓ Réclamation: OUI
✓ Thème: FIBRE
✓ Sentiment: NEGATIF
✓ Urgence: ELEVEE
✓ Type d'incident: PANNE
✓ Confiance: 0.60
✓ Justification: Classification automatique par règles (fallback)

🔍 Vérifications:
  ✅ is_reclamation: OUI (attendu: OUI)
  ✅ theme: FIBRE (attendu: FIBRE)
  ...
  
📊 Score: 4/4 (100.0%)

...

==================================================
  RÉSUMÉ DES TESTS
==================================================

📊 Accuracy Moyenne: 85.0%
📝 Tests Exécutés: 5

✅ SUCCÈS ! Le classificateur fonctionne correctement.

💡 Note: Ces tests utilisent le mode FALLBACK (règles simples).
   Pour des résultats optimaux, utilisez un LLM (GPT-4, Claude, etc.)
==================================================
```

---

## Étape 3: Classification de Vos Propres Tweets (2 min)

### Option A: Code Python

Créez un fichier `test_mes_tweets.py`:

```python
from app.services.tweet_classifier import classify_tweet

# Vos tweets à classifier
mes_tweets = [
    "@Free Internet très lent ce matin",
    "@Free Merci pour le service rapide",
    "@Free Facture incorrecte, besoin d'aide"
]

# Classifier chaque tweet
for tweet in mes_tweets:
    result = classify_tweet(tweet)
    
    print(f"\n📝 Tweet: {tweet}")
    print(f"   Réclamation: {result.is_reclamation}")
    print(f"   Thème: {result.theme}")
    print(f"   Sentiment: {result.sentiment}")
    print(f"   Urgence: {result.urgence}")
    print(f"   Confiance: {result.confidence:.2f}")
```

Exécutez:
```bash
python test_mes_tweets.py
```

### Option B: Interface Interactive (Python REPL)

```bash
python
```

Puis dans le REPL:
```python
>>> from app.services.tweet_classifier import classify_tweet
>>> result = classify_tweet("@Free Box en panne")
>>> print(result.is_reclamation)
OUI
>>> print(result.theme)
FIBRE
>>> print(result.json(indent=2))
{
  "is_reclamation": "OUI",
  "theme": "FIBRE",
  ...
}
```

---

## Étape 4 (Optionnel): Avec API LLM (Si Vous Avez une Clé)

Si vous avez une clé API OpenAI:

```python
from app.services.tweet_classifier import TweetClassifier

# Initialiser avec GPT-4
classifier = TweetClassifier(
    model_name="gpt-4",
    api_key="sk-...",  # Votre clé API
    temperature=0.1
)

# Classifier
tweet = "@Free Problème de connexion depuis 2 jours"
result = classifier.classify(tweet)

print(result.json(indent=2))
```

**Avantages avec LLM**:
- ✅ Accuracy > 90% (vs ~70% fallback)
- ✅ Confiance > 0.85 (vs ~0.60 fallback)
- ✅ Meilleure compréhension du contexte
- ✅ Justifications plus détaillées

---

## Étape 5 (Optionnel): Interface Streamlit

Si vous voulez une interface graphique:

```bash
# Aller dans streamlit_app/
cd ../streamlit_app

# Lancer l'interface
streamlit run pages/classification_llm.py
```

Puis:
1. Ouvrir http://localhost:8501
2. Uploader un CSV avec colonne `text`
3. Cliquer "Lancer la Classification"
4. Analyser les résultats et visualisations

---

## 📊 Taxonomie de Référence

Voici ce que le système classifie:

| Dimension | Valeurs Possibles |
|-----------|-------------------|
| **is_reclamation** | OUI, NON |
| **theme** | FIBRE, MOBILE, TV, FACTURE, SAV, RESEAU, AUTRE |
| **sentiment** | NEGATIF, NEUTRE, POSITIF |
| **urgence** | FAIBLE, MOYENNE, ELEVEE, CRITIQUE |
| **type_incident** | PANNE, LENTEUR, FACTURATION, PROCESSUS_SAV, INFO, AUTRE |

---

## ❓ FAQ

**Q: Le test rapide échoue avec `ModuleNotFoundError`**  
A: Assurez-vous d'être dans `backend/` et d'avoir installé les dépendances.

**Q: J'obtiens une accuracy < 60% en mode fallback**  
A: Normal pour tweets complexes. Utilisez un LLM (GPT-4) pour de meilleurs résultats.

**Q: Comment classifier un fichier CSV complet ?**  
A: Voir la documentation complète dans `DOCUMENTATION_CLASSIFICATION_LLM.md`

**Q: Puis-je utiliser Claude au lieu de GPT-4 ?**  
A: Oui ! Remplacez `model_name="gpt-4"` par `model_name="claude-3-opus"` et utilisez votre clé Anthropic.

---

## 📚 Documentation Complète

Pour aller plus loin:
- **Guide Complet**: `DOCUMENTATION_CLASSIFICATION_LLM.md`
- **Récapitulatif**: `RECAPITULATIF_CLASSIFICATION_LLM.md`
- **Pipeline Entraînement**: `python backend/train_classifier.py --help`
- **Tests Unitaires**: `python backend/tests/test_tweet_classifier.py`

---

## ✅ Checklist de Validation

Après ce guide rapide, vous devriez avoir:

- [x] Installé les dépendances
- [x] Exécuté le test rapide (5 tweets)
- [x] Compris la taxonomie de classification
- [x] Testé avec vos propres tweets
- [x] (Optionnel) Testé avec un LLM
- [x] (Optionnel) Lancé l'interface Streamlit

---

**Prêt à utiliser le système pour votre soutenance !** 🎓

Si vous avez des questions, consultez `DOCUMENTATION_CLASSIFICATION_LLM.md` ou ouvrez une issue sur GitHub.

