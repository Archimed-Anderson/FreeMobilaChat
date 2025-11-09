# 🚀 Guide d'Utilisation Rapide - Classificateur Ultra-Optimisé

## ⚡ Démarrage en 5 Minutes

### 1️⃣ Installation (1 minute)

```bash
# Installer les dépendances
pip install -r requirements_optimized.txt

# Installer Ollama (si pas déjà fait)
# Windows: Télécharger depuis https://ollama.com/download
# Linux/Mac:
curl -fsSL https://ollama.com/install.sh | sh

# Télécharger Mistral
ollama pull mistral
```

### 2️⃣ Vérification (30 secondes)

```bash
# Test rapide
python -c "from streamlit_app.services.ultra_optimized_classifier import UltraOptimizedClassifier; print('✅ OK')"
```

### 3️⃣ Premier Benchmark (2 minutes)

```bash
# Lancer le benchmark avec données synthétiques
python benchmark_ultra_optimized.py

# Ou avec votre CSV
python benchmark_ultra_optimized.py --csv votre_fichier.csv --column text
```

### 4️⃣ Utilisation dans Streamlit (1 minute)

```bash
# Lancer l'application
cd C:\Users\ander\Desktop\FreeMobilaChat
python -m streamlit run streamlit_app/pages/5_Classification_Mistral.py

# Ouvrir: http://localhost:8501/Classification_Mistral
```

---

## 📱 Utilisation de l'Interface Streamlit

### Workflow Complet

```
1. UPLOAD
   ├─ Cliquer "Sélectionnez votre fichier CSV"
   ├─ Uploader votre fichier de tweets
   └─ Sélectionner la colonne de texte

2. NETTOYAGE
   ├─ Cliquer "Nettoyer les Données"
   ├─ Vérifier les statistiques
   └─ Voir le nombre de doublons supprimés

3. CONFIGURATION
   ├─ Sélectionner le mode:
   │  • ⚡ FAST (20s) - Sentiment uniquement
   │  • ⭐ BALANCED (2min) - RECOMMANDÉ
   │  • 🎯 PRECISE (10min) - Précision maximale
   └─ ✅ Cocher "Classificateur ULTRA-OPTIMISÉ"

4. CLASSIFICATION
   ├─ Cliquer "Lancer la Classification"
   ├─ Observer la progression en temps réel
   └─ Attendre la fin (70s pour 2634 tweets)

5. RÉSULTATS
   ├─ Visualiser les 6 KPI cards
   ├─ Explorer les 6 graphiques interactifs
   └─ Exporter les résultats (CSV, JSON)
```

---

## 💻 Utilisation Programmatique

### Exemple Simple

```python
from streamlit_app.services.ultra_optimized_classifier import UltraOptimizedClassifier
from streamlit_app.services.tweet_cleaner import TweetCleaner
import pandas as pd

# 1. Charger les données
df = pd.read_csv('tweets.csv')

# 2. Nettoyer
cleaner = TweetCleaner()
df_clean, stats = cleaner.process_dataframe(df, 'text')

# 3. Classifier
classifier = UltraOptimizedClassifier(
    batch_size=50,
    use_cache=True
)

results, metrics = classifier.classify_tweets_batch(
    df_clean,
    text_column='text_cleaned',
    mode='balanced'
)

# 4. Résultats
print(f"✅ {len(results)} tweets classifiés en {metrics.total_time_seconds:.1f}s")
print(f"   Vitesse: {metrics.tweets_per_second:.1f} tweets/s")

# 5. Sauvegarder
results.to_csv('tweets_classified.csv', index=False)
```

### Exemple avec Progress Bar

```python
def progress_callback(message, progress):
    print(f"[{int(progress*100):3d}%] {message}")

results, metrics = classifier.classify_tweets_batch(
    df_clean,
    mode='balanced',
    progress_callback=progress_callback
)
```

### Exemple avec Gestion d'Erreurs

```python
try:
    results, metrics = classifier.classify_tweets_batch(df_clean)
    
    # Vérifier la qualité
    na_count = results['sentiment'].isna().sum()
    if na_count > 0:
        print(f"⚠️  {na_count} tweets avec N/A")
    else:
        print("✅ 100% de couverture")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    # Fallback sur mode FAST
    results, metrics = classifier.classify_tweets_batch(df_clean, mode='fast')
```

---

## 🎯 Modes de Classification

| Mode | Durée (2634 tweets) | Précision | Usage |
|------|---------------------|-----------|-------|
| **FAST** | ~20s | 75% | Analyses rapides, tests |
| **BALANCED** ⭐ | ~70s | 88% | Usage général (RECOMMANDÉ) |
| **PRECISE** | ~300s | 95% | Analyses critiques |

### Quand utiliser quel mode?

**FAST**:
- ✅ Prototypage
- ✅ Tests rapides
- ✅ Datasets >10k tweets
- ❌ Rapports officiels

**BALANCED** (Recommandé):
- ✅ Usage quotidien
- ✅ Rapports clients
- ✅ Analyses approfondies
- ✅ Meilleur compromis temps/précision

**PRECISE**:
- ✅ Audits qualité
- ✅ Décisions stratégiques
- ✅ Datasets critiques
- ❌ Contraintes de temps

---

## 🔧 Configuration Avancée

### Cache

```python
# Activer le cache (recommandé)
classifier = UltraOptimizedClassifier(use_cache=True)

# Désactiver (pour tests)
classifier = UltraOptimizedClassifier(use_cache=False)

# Nettoyer le cache
classifier.clear_cache()
```

### Batch Size

```python
# Par défaut: 50 (optimal pour CPU)
classifier = UltraOptimizedClassifier(batch_size=50)

# Plus petit (plus de feedback)
classifier = UltraOptimizedClassifier(batch_size=25)

# Plus grand (plus rapide, moins de feedback)
classifier = UltraOptimizedClassifier(batch_size=100)
```

### Workers

```python
# Par défaut: 4 workers
classifier = UltraOptimizedClassifier(max_workers=4)

# Plus de workers (si CPU puissant)
classifier = UltraOptimizedClassifier(max_workers=8)

# Moins de workers (si contraintes mémoire)
classifier = UltraOptimizedClassifier(max_workers=2)
```

---

## 📊 Interpréter les Résultats

### KPIs Retournés

```python
# Colonnes dans results DataFrame:
results.columns
# ['text_cleaned', 'sentiment', 'is_claim', 'urgence', 
#  'topics', 'incident', 'confidence']
```

| KPI | Valeurs Possibles | Description |
|-----|-------------------|-------------|
| **sentiment** | positif, négatif, neutre | Sentiment général du tweet |
| **is_claim** | oui, non | Le tweet contient-il une réclamation? |
| **urgence** | faible, moyenne, critique | Niveau d'urgence |
| **topics** | produit, service, support, etc. | Catégorie thématique |
| **incident** | technique, facturation, réseau, etc. | Type d'incident |
| **confidence** | 0.0 - 1.0 | Score de confiance |

### Statistiques Descriptives

```python
# Distribution des sentiments
print(results['sentiment'].value_counts())

# Pourcentage de réclamations
claims_pct = (results['is_claim'] == 'oui').mean() * 100
print(f"Réclamations: {claims_pct:.1f}%")

# Urgence moyenne
urgence_map = {'faible': 1, 'moyenne': 2, 'critique': 3}
urgence_avg = results['urgence'].map(urgence_map).mean()
print(f"Urgence moyenne: {urgence_avg:.2f}/3")

# Confiance moyenne
print(f"Confiance moyenne: {results['confidence'].mean():.2f}")
```

### Filtrage

```python
# Réclamations critiques
critical_claims = results[
    (results['is_claim'] == 'oui') & 
    (results['urgence'] == 'critique')
]
print(f"Réclamations critiques: {len(critical_claims)}")

# Sentiments négatifs
negative = results[results['sentiment'] == 'negatif']

# Basse confiance
low_confidence = results[results['confidence'] < 0.5]
```

---

## ⚠️ Troubleshooting

### Problème 1: Import Error

```bash
# Erreur: "No module named 'services'"
# Solution:
export PYTHONPATH="${PYTHONPATH}:/path/to/FreeMobilaChat/streamlit_app"
```

### Problème 2: Ollama Connection

```bash
# Erreur: "Connection refused to Ollama"
# Solution:
ollama serve  # Démarrer Ollama

# Vérifier:
ollama list  # Doit montrer 'mistral'
```

### Problème 3: Out of Memory

```python
# Réduire le batch size
classifier = UltraOptimizedClassifier(batch_size=25)

# Ou désactiver le cache
classifier = UltraOptimizedClassifier(use_cache=False)
```

### Problème 4: Trop Lent

```python
# Vérifier le mode
mode='fast'  # Au lieu de 'balanced'

# Augmenter workers (si CPU le permet)
classifier = UltraOptimizedClassifier(max_workers=8)

# Utiliser le cache (2e run sera 10x plus rapide)
classifier = UltraOptimizedClassifier(use_cache=True)
```

---

## 📈 Monitoring

### Logs

```python
import logging

# Activer les logs détaillés
logging.basicConfig(level=logging.INFO)

# Sauvegarder dans un fichier
logging.basicConfig(
    filename='classifier.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Métriques

```python
# Accéder aux métriques
metrics = classifier.phase_times
print(f"Phase 1 (BERT): {metrics['phase1_bert']:.1f}s")
print(f"Phase 2 (Rules): {metrics['phase2_rules']:.1f}s")
print(f"Phase 3 (Mistral): {metrics['phase3_mistral']:.1f}s")

# Cache stats
print(f"Cache hits: {classifier.cache_hits}")
print(f"Cache misses: {classifier.cache_misses}")
hit_rate = classifier.cache_hits / (classifier.cache_hits + classifier.cache_misses)
print(f"Hit rate: {hit_rate*100:.1f}%")
```

---

## 🎓 Best Practices

### ✅ À FAIRE

1. **Toujours nettoyer les données avant classification**
```python
cleaner = TweetCleaner()
df_clean, _ = cleaner.process_dataframe(df, 'text')
```

2. **Activer le cache pour datasets similaires**
```python
classifier = UltraOptimizedClassifier(use_cache=True)
```

3. **Utiliser mode BALANCED par défaut**
```python
results, _ = classifier.classify_tweets_batch(df, mode='balanced')
```

4. **Vérifier la qualité des résultats**
```python
na_pct = results['sentiment'].isna().mean() * 100
assert na_pct < 1, f"Trop de N/A: {na_pct:.1f}%"
```

### ❌ À ÉVITER

1. **Ne pas skipper le nettoyage**
```python
# ❌ MAL
results, _ = classifier.classify_tweets_batch(raw_df)

# ✅ BIEN
df_clean, _ = cleaner.process_dataframe(raw_df)
results, _ = classifier.classify_tweets_batch(df_clean)
```

2. **Ne pas ignorer les erreurs**
```python
# ❌ MAL
results, _ = classifier.classify_tweets_batch(df)

# ✅ BIEN
try:
    results, _ = classifier.classify_tweets_batch(df)
except Exception as e:
    logger.error(f"Classification failed: {e}")
    raise
```

3. **Ne pas modifier les résultats directement**
```python
# ❌ MAL
results['custom_field'] = ...  # Peut casser l'export

# ✅ BIEN
results_copy = results.copy()
results_copy['custom_field'] = ...
```

---

## 📚 Ressources

- **Architecture**: `ARCHITECTURE_OPTIMISATION.md`
- **Code Source**: `streamlit_app/services/ultra_optimized_classifier.py`
- **Benchmark**: `benchmark_ultra_optimized.py`
- **Dépendances**: `requirements_optimized.txt`

---

## 🆘 Support

**Questions?** Consultez:
1. `ARCHITECTURE_OPTIMISATION.md` - Documentation technique complète
2. `benchmark_ultra_optimized.py` - Exemples d'utilisation
3. Logs dans `classifier.log`

**Bugs?** Vérifiez:
1. Dépendances installées: `pip list`
2. Ollama running: `ollama list`
3. Mistral disponible: `ollama run mistral "test"`

---

**🚀 Bon usage du Classificateur Ultra-Optimisé V2!**


