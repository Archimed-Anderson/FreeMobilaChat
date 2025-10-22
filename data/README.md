# Répertoire de Données - FreeMobilaChat

## Important

Ce répertoire contient les données d'entraînement et de test pour le projet FreeMobilaChat. Les fichiers de données ne sont **pas** versionnés dans Git pour des raisons de taille et de confidentialité.

## Structure des Données

```
data/
├── raw/                    # Données brutes (CSV, Excel)
│   └── [Ajoutez vos fichiers CSV/Excel ici]
│
├── processed/              # Données nettoyées
│
├── training/               # Jeux de données d'entraînement
│   ├── train_dataset.csv
│   ├── validation_dataset.csv
│   └── test_dataset.csv
│
├── samples/                # Échantillons de données pour tests
│   └── sample_tweets.csv
│
└── fast_graphrag/          # Cache GraphRAG
```

## Fichiers Requis pour l'Entraînement

Pour entraîner les modèles, vous devez avoir dans `data/training/` :

1. **train_dataset.csv** - Ensemble d'entraînement (70% des données)
2. **validation_dataset.csv** - Ensemble de validation (15% des données)
3. **test_dataset.csv** - Ensemble de test (15% des données)

### Format des Fichiers CSV

Colonnes requises :
- `tweet_id` : Identifiant unique du tweet
- `author` : Auteur du tweet
- `text` : Contenu du tweet
- `date` : Date de publication
- `sentiment` : Sentiment (positif, neutre, negatif)
- `category` : Catégorie (sav, technique, commercial, autre)
- `priority` : Priorité (haute, moyenne, basse)

## Note pour Streamlit Cloud

Les fichiers de données locaux ne sont **pas nécessaires** pour le déploiement sur Streamlit Cloud. L'application peut fonctionner sans ces fichiers et permettra aux utilisateurs de télécharger leurs propres données.

## Ajout de Nouvelles Données

1. Placez vos fichiers CSV/Excel dans `data/raw/`
2. Les fichiers seront automatiquement ignorés par Git (`.gitignore`)
3. Utilisez l'interface Streamlit pour analyser les données

---

**Note** : Ne jamais commiter de fichiers `.csv`, `.xlsx`, `.db`, `.pkl` dans le repository Git.
