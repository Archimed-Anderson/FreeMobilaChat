# Classification Automatique - Documentation

## Fonctionnalités

Cette page de classification automatique offre une analyse complète des fichiers CSV uploadés avec les fonctionnalités suivantes :

### 1. Analyse Automatique et Dynamique
- **Intégration ydata-profiling** : Génération d'une analyse statistique complète des fichiers CSV téléchargés
- **Classification automatique des colonnes** : Détection intelligente des types de données (numérique, catégorielle, temporelle, texte)
- **Détection automatique des indicateurs clés** : Identification des corrélations, distributions et outliers
- **Scoring de qualité des données** : Métriques de complétude, unicité et cohérence

### 2. Dashboard Dynamique et Interactif
- **Visualisations interactives** : Création de graphiques modernes avec Plotly
- **Métriques automatiques** : Adaptées au type de données détecté
- **Graphiques adaptatifs** : Histogrammes, scatter plots, heatmaps, box plots selon les données
- **Synthèse d'insights** : Basée sur les patterns détectés dans les données

## Utilisation

1. Accédez à la page "Classification" dans l'application Streamlit
2. Uploadez un fichier CSV, Excel ou JSON
3. L'analyse automatique commence immédiatement
4. Explorez les différents onglets :
   - **Dashboard** : Résumé des insights et score de qualité
   - **Visualisations** : Graphiques interactifs adaptés aux données
   - **Insights** : Analyse approfondie contextuelle
   - **Rapport Complet** : Rapport d'analyse statistique détaillé

## Technologies Utilisées

- **ydata-profiling** : Pour l'analyse statistique automatique
- **Plotly** : Pour les visualisations interactives
- **Streamlit** : Interface utilisateur moderne
- **Pandas/Numpy** : Traitement des données

## Fonctionnalités Avancées

### Détection Intelligente des Types de Colonnes
- Numérique : Valeurs continues ou discrètes
- Catégorielle : Valeurs avec faible cardinalité
- Temporelle : Dates et timestamps
- Texte : Données textuelles avec haute cardinalité

### Analyse de Qualité des Données
- **Complétude** : Pourcentage de valeurs non manquantes
- **Unicité** : Pourcentage de valeurs uniques
- **Cohérence** : Cohérence des types de données
- **Score global** : Note globale de qualité sur 100

### Insights Automatiques
- Corrélations fortes entre variables
- Valeurs dominantes dans les colonnes catégorielles
- Détection d'outliers statistiques
- Patterns récurrents dans les données

## Personnalisation

Le système s'adapte automatiquement aux caractéristiques spécifiques de chaque fichier CSV téléchargé :
- Types de visualisations adaptés aux données
- Métriques pertinentes selon le domaine métier détecté
- Recommendations personnalisées selon la qualité des données