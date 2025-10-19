# README - Rapport Bloc CC2.1

## 📋 Vue d'Ensemble

Ce dossier contient le rapport complet du **Bloc CC2.1** pour le projet **FreeMobilaChat**, couvrant le nettoyage, la structuration et l'analyse des données utilisées pour l'entraînement du chatbot SAV intelligent.

## 📁 Fichiers Inclus

```
.
├── Rapport_Bloc_CC2.1_FreeMobilaChat.md    # Rapport complet (format Markdown)
├── generate_visualizations.py               # Script de génération des graphiques
├── README_Rapport_CC2.1.md                  # Ce fichier
└── visualizations/                          # Dossier des visualisations générées
    ├── 1_distribution_sentiments.png
    ├── 2_distribution_categories.png
    ├── 3_distribution_priorites.png
    ├── 4_correlation_sentiment_categorie.png
    ├── 5_distribution_longueur_textes.png
    ├── 6_evolution_temporelle.png
    ├── 7_nuages_mots_sentiments.png
    └── 8_kpi_operationnels.png
```

## 📊 Contenu du Rapport

Le rapport est structuré en **6 sections principales** :

### 1. Introduction
- Contexte du projet FreeMobilaChat
- Objectifs de l'analyse
- Source et volume des données (3,764 tweets)

### 2. Nettoyage et Structuration des Données
- Architecture du pipeline de nettoyage
- Processus de nettoyage détaillé (HTML, Unicode, URLs, etc.)
- Création des labels de vérité terrain (sentiment, catégorie, priorité)
- Séparation stratifiée des données (70/10/20)
- Structure finale des datasets

### 3. Définition et Calcul des KPI
- **KPI de Volume et Distribution**
  - Volume total par split
  - Distribution du sentiment (78% neutral, 14% negative, 8% positive)
  - Distribution des catégories (8 catégories)
  - Distribution des priorités (4 niveaux)
  
- **KPI de Qualité Textuelle**
  - Longueur moyenne des textes (~150 caractères)
  - Diversité des auteurs (ratio 0.76)
  
- **KPI Opérationnels**
  - Tweets nécessitant une réponse (94%)
  - Tweets urgents (17.5%)
  - Temps de résolution estimé (moyenne: 35 minutes)
  
- **KPI de Cohérence des Splits**
  - Écart maximum entre splits < 2%

### 4. Exploration Visuelle
- 8 types de visualisations recommandées
- Analyse des patterns et corrélations
- Insights et interprétations

### 5. Qualité des Données
- Évaluation de la complétude (100%)
- Cohérence des labels (100%)
- Détection des outliers et duplicatas
- Équilibre des classes (déséquilibre modéré à fort)
- Garanties de qualité mises en place
- Limitations et améliorations futures

### 6. Conclusion
- Synthèse des résultats
- Qualité globale: **4.6/5 ⭐**
- Prochaines étapes (entraînement des modèles)
- Impact attendu

## 🚀 Génération des Visualisations

### Prérequis

Installer les dépendances nécessaires :

```bash
pip install pandas matplotlib seaborn wordcloud
```

### Exécution

```bash
# Depuis la racine du projet FreeMobilaChat
python generate_visualizations.py
```

### Résultat

Le script génère **8 visualisations** dans le dossier `visualizations/` :

1. **Distribution des Sentiments** - Diagramme en barres comparant les 3 splits
2. **Distribution des Catégories** - Diagramme en barres horizontales (Training Set)
3. **Distribution des Priorités** - Diagramme circulaire (Training Set)
4. **Corrélation Sentiment-Catégorie** - Heatmap de contingence
5. **Distribution de la Longueur des Textes** - Histogramme + Boxplot
6. **Évolution Temporelle** - Série temporelle du volume et des sentiments
7. **Nuages de Mots par Sentiment** - 3 word clouds (positive, negative, neutral)
8. **KPI Opérationnels** - 4 graphiques (réponse, urgence, temps, diversité)

### Temps d'Exécution

- **Durée estimée:** 30-60 secondes
- **Taille des fichiers:** ~5-10 MB au total
- **Résolution:** 300 DPI (haute qualité)

## 📈 Statistiques Clés

### Volume des Données

| Split | Échantillons | Pourcentage |
|-------|--------------|-------------|
| Training | 2,634 | 70% |
| Validation | 377 | 10% |
| Test | 753 | 20% |
| **TOTAL** | **3,764** | **100%** |

### Distribution du Sentiment (Training Set)

| Sentiment | Count | Pourcentage |
|-----------|-------|-------------|
| Neutral | 2,058 | 78.1% |
| Negative | 389 | 14.8% |
| Positive | 187 | 7.1% |

### Top 5 Catégories (Training Set)

1. **Autre:** 44.9% (1,182 tweets)
2. **Question:** 26.2% (689 tweets)
3. **Technique:** 6.9% (183 tweets)
4. **Réseau:** 6.1% (161 tweets)
5. **Compliment:** 6.1% (160 tweets)

### Priorités (Training Set)

| Priorité | Count | Pourcentage |
|----------|-------|-------------|
| Basse | 1,987 | 75.4% |
| Haute | 369 | 14.0% |
| Moyenne | 162 | 6.2% |
| Critique | 116 | 4.4% |

## 🔍 Points Clés du Rapport

### ✅ Forces

1. **Pipeline Robuste**
   - Nettoyage automatisé et reproductible
   - Gestion complète des cas limites
   - Traçabilité totale

2. **Labellisation Systématique**
   - 3,764 tweets labellisés sur 3 dimensions
   - Règles heuristiques cohérentes
   - Labels dérivés pour l'opérationnalisation

3. **Qualité des Datasets**
   - 100% de complétude (aucune valeur manquante)
   - Cohérence inter-splits validée
   - Split stratifié respecté

4. **Analyse Approfondie**
   - 15+ KPI calculés et documentés
   - Patterns et corrélations identifiés
   - Recommandations d'amélioration

### ⚠️ Limitations

1. **Labellisation Heuristique**
   - Labels générés par règles, pas par annotation humaine
   - Précision potentiellement inférieure
   - **Mitigation:** Validation par échantillonnage manuel

2. **Déséquilibre des Classes**
   - Forte disparité (ratio jusqu'à 112:1)
   - Biais potentiel vers classes majoritaires
   - **Mitigation:** Class weights, SMOTE, métriques adaptées

3. **Couverture Temporelle**
   - Données sur 12 mois seulement
   - Possibles biais saisonniers
   - **Mitigation:** Collecte continue

## 🎯 Recommandations

### Court Terme (1-3 mois)

1. **Annotation Manuelle**
   - Valider 500-1000 tweets manuellement
   - Calculer l'accord inter-annotateurs
   - Ajuster les règles de labellisation

2. **Augmentation de Données**
   - Paraphrasing pour classes minoritaires
   - Back-translation (FR → EN → FR)
   - Génération synthétique avec LLM

3. **Enrichissement des Features**
   - Extraction d'entités nommées (NER)
   - Analyse de sentiment fine-grained
   - Détection d'émotions

### Moyen Terme (3-6 mois)

1. **Active Learning**
   - Sélection intelligente des tweets à annoter
   - Annotation itérative des cas difficiles

2. **Collecte Supplémentaire**
   - Extension à d'autres sources (Facebook, email)
   - Augmentation du volume (objectif: 10,000+ tweets)

3. **Validation Externe**
   - Comparaison avec datasets publics
   - Benchmarking avec modèles pré-entraînés

### Long Terme (6-12 mois)

1. **Pipeline de Production**
   - Collecte automatique et continue
   - Labellisation semi-automatique
   - Monitoring de la qualité en temps réel

2. **Feedback Loop**
   - Intégration des retours utilisateurs
   - Correction des erreurs de prédiction
   - Amélioration continue

## 📚 Références

### Code Source

- **Module de nettoyage:** `backend/app/utils/cleaning.py`
- **Service de préparation:** `backend/app/services/data_preparation.py`
- **Pipeline complet:** `backend/run_complete_pipeline.py`

### Datasets

- **Training:** `data/training/train_dataset.csv`
- **Validation:** `data/training/validation_dataset.csv`
- **Test:** `data/training/test_dataset.csv`
- **Statistiques:** `data/training/dataset_statistics.json`

### Bibliothèques

- **pandas** 2.2.0+ - Manipulation de données
- **numpy** 2.0.0+ - Calculs numériques
- **scikit-learn** 1.5.2+ - Split stratifié
- **matplotlib** 3.9.0+ - Visualisations
- **seaborn** 0.13.0+ - Visualisations statistiques
- **wordcloud** 1.9.0+ - Nuages de mots

## 📞 Contact

**Auteur:** Anderson Archimède  
**Email:** andersonarchimede@gmail.com  
**Projet:** FreeMobilaChat  
**Date:** 18 Octobre 2025

## 📄 Licence

Ce rapport et les scripts associés font partie du projet FreeMobilaChat et sont destinés à un usage académique dans le cadre du Bloc CC2.1.

---

**Note:** Pour toute question ou clarification sur le rapport, n'hésitez pas à me contacter.

