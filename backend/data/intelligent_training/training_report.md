
# Rapport d'Entraînement du Classificateur de Tweets

**Date:** 2025-10-23 22:17:20
**Dataset:** ../data/raw/free_tweet_export.csv

## Résumé des Performances

### Métriques Globales
- **Total tweets analysés:** 3,738
- **Taux de réclamation moyen:** 2.9%
- **Confiance moyenne:** 0.59

### Performance par Split

#### Entraînement (2,616 tweets)
- Réclamations détectées: 63 (2.4%)
- Confiance moyenne: 0.59
- Précision: N/A
- Rappel: N/A
- F1-Score: N/A

#### Validation (560 tweets)
- Réclamations détectées: 18 (3.2%)
- Confiance moyenne: 0.59
- Précision: N/A
- Rappel: N/A
- F1-Score: N/A

#### Test (562 tweets)
- Réclamations détectées: 18 (3.2%)
- Confiance moyenne: 0.60
- Précision: N/A
- Rappel: N/A
- F1-Score: N/A

## Distribution des Classifications

### Thèmes (Test)
- **FIBRE:** 251 tweets (44.7%)
- **MOBILE:** 29 tweets (5.2%)
- **AUTRE:** 196 tweets (34.9%)
- **RESEAU:** 6 tweets (1.1%)
- **FACTURE:** 17 tweets (3.0%)
- **SAV:** 41 tweets (7.3%)
- **TV:** 22 tweets (3.9%)

### Sentiments (Test)
- **NEUTRE:** 482 tweets (85.8%)
- **NEGATIF:** 20 tweets (3.6%)
- **POSITIF:** 60 tweets (10.7%)

### Niveaux d'Urgence (Test)
- **FAIBLE:** 408 tweets (72.6%)
- **MOYENNE:** 82 tweets (14.6%)
- **CRITIQUE:** 52 tweets (9.3%)
- **ELEVEE:** 20 tweets (3.6%)

## Recommandations

1. **Qualité des données:** Le classificateur montre une confiance moyenne de 0.60
2. **Détection des réclamations:** 3.2% des tweets sont classés comme réclamations
3. **Amélioration continue:** Surveiller les performances sur de nouveaux datasets

## Fichiers Générés

- `train_classifications.csv`: Classifications d'entraînement
- `val_classifications.csv`: Classifications de validation  
- `test_classifications.csv`: Classifications de test
- `metrics.json`: Métriques détaillées
- `training_report.md`: Ce rapport

---
*Généré automatiquement par le système d'entraînement FreeMobilaChat*
