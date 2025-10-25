# Classification Automatique - Guide d'Utilisation

## Description

Cette page permet d'analyser automatiquement les fichiers CSV uploadés avec les fonctionnalités suivantes :

1. **Analyse Statistique Complète** : Utilisation de ydata-profiling pour générer un rapport d'analyse détaillé
2. **Classification Automatique des Colonnes** : Détection intelligente des types de données
3. **Détection d'Indicateurs Clés** : Identification des corrélations, distributions et outliers
4. **Dashboard Interactif** : Visualisations avec Plotly adaptées aux données

## Fonctionnalités

### Analyse Automatique
- Intégration avec ydata-profiling pour une analyse statistique complète
- Classification automatique des colonnes (numérique, catégorielle, temporelle, texte)
- Détection automatique des indicateurs clés
- Scoring de qualité des données (complétude, unicité, cohérence)

### Visualisations Interactives
- Histogrammes pour les données numériques
- Diagrammes circulaires pour les données catégorielles
- Graphiques temporels pour les séries chronologiques
- Matrices de corrélation
- Box plots pour la détection d'outliers

### Insights Automatiques
- Résumé des patterns détectés
- Corrélations fortes
- Valeurs dominantes
- Données aberrantes

## Utilisation

1. Accédez à la page "Classification" dans l'application Streamlit
2. Uploadez un fichier CSV, Excel ou JSON
3. L'analyse commence automatiquement
4. Explorez les différents onglets :
   - **Dashboard** : Vue d'ensemble et score de qualité
   - **Visualisations** : Graphiques interactifs
   - **Insights** : Analyse approfondie
   - **Rapport Complet** : Rapport ydata-profiling détaillé

## Types de Colonnes Détectés

- **Numeric** : Valeurs numériques continues ou discrètes
- **Categorical** : Valeurs avec faible cardinalité
- **Temporal** : Dates et timestamps
- **Text** : Données textuelles avec haute cardinalité

## Indicateurs de Qualité

- **Complétude** : Pourcentage de valeurs non manquantes
- **Unicité** : Pourcentage de valeurs uniques
- **Cohérence** : Cohérence des types de données
- **Score Global** : Note globale de qualité sur 100

## Technologies Utilisées

- **ydata-profiling** : Analyse statistique automatique
- **Plotly** : Visualisations interactives
- **Streamlit** : Interface utilisateur
- **Pandas/Numpy** : Traitement des données

## Personnalisation

Le système s'adapte automatiquement aux caractéristiques spécifiques de chaque fichier CSV téléchargé :
- Types de visualisations adaptés aux données
- Métriques pertinentes selon le domaine métier détecté
- Recommendations personnalisées selon la qualité des données