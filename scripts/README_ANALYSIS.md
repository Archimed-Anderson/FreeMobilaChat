# Analyse Académique des Tweets Free Mobile - Guide d'Utilisation

## 📋 Contexte

Ce dossier contient le code Python pour l'analyse académique de ~5000 tweets Free Mobile dans le cadre du mémoire de master.

---

## 🎯 Objectifs

- Analyser les tweets SAV Free Mobile
- Extraire sentiments, thèmes et urgences
- Calculer KPIs métier
- Générer rapport PDF académique (5+ pages)

---

## 📁 Structure des Scripts

```
scripts/
├── run_complete_analysis.py    # Script principal - EXÉCUTER CELUI-CI
├── part1_cleaning.py            # Nettoyage et enrichissement
├── part2_analysis_viz.py        # KPIs et visualisations
├── generate_report.py           # Génération rapport PDF
└── README_ANALYSIS.md           # Ce fichier
```

---

## 🚀 Installation des Dépendances

```bash
pip install pandas numpy matplotlib seaborn wordcloud scikit-learn reportlab squarify
```

---

## 📊 Préparation des Données

1. **Placer votre fichier CSV** dans `data/raw/free_tweet_export.csv`

2. **Colonnes attendues** (ajustement automatique si différent):
   - `tweet_id` ou `id`
   - `created_at` ou `timestamp`
   - `text` ou `tweet_text`
   - `lang` ou `language`
   - `is_retweet`

3. **Si le fichier n'existe pas**: Un dataset de démonstration sera créé automatiquement

---

## ▶️ Exécution

### Option 1: Exécution Complète (RECOMMANDÉE)

```bash
# Depuis la racine du projet
python scripts/run_complete_analysis.py
```

Cette commande exécute automatiquement les 3 étapes:
1. Nettoyage et enrichissement
2. Calcul KPIs et visualisations
3. Génération rapport PDF

### Option 2: Exécution Étape par Étape

```bash
# Étape 1: Nettoyage
python scripts/part1_cleaning.py

# Étape 2: Analyse et visualisations
python scripts/part2_analysis_viz.py

# Étape 3: Rapport PDF
python scripts/generate_report.py
```

---

## 📦 Livrables Générés

### 1. Données Nettoyées
**Fichier**: `data/processed/cleaned_data.csv`

**Colonnes ajoutées**:
- `clean_text` - Texte nettoyé
- `sentiment` - négatif / neutre / positif
- `dominant_keyword` - Mot-clé TF-IDF principal
- `theme` - technique / réseau / facture / service_client / autre
- `is_urgent` - True/False

### 2. KPIs (JSON)
**Fichier**: `data/processed/kpis.json`

**Contenu**:
- Volume total de tweets
- Distribution des sentiments (%)
- Top 5 thèmes
- Pourcentage de tweets urgents
- Top 20 mots-clés négatifs

### 3. Visualisations (PNG - 300 DPI)
**Dossier**: `figures/`

**10 visualisations académiques professionnelles**:
- `01_volume_jour.png` - Volume quotidien avec moyenne mobile
- `02_distribution_sentiments.png` - Distribution sentiments (bar chart annoté)
- `03_wordcloud_negatifs.png` - Nuage de mots (tweets négatifs, TF-IDF)
- `04_treemap_themes.png` - Répartition thématique (treemap)
- `05_heatmap_horaire.png` - Heatmap temporelle (jour × heure)
- `06_evolution_sentiments.png` - Évolution temporelle sentiments (line chart)
- `07_top_keywords.png` - Top 10 mots-clés dominants (horizontal bar)
- `08_themes_sentiments.png` - Thèmes × Sentiments (stacked bar)
- `09_urgence_themes.png` - Urgences par thème (pie chart)
- `10_distribution_horaire.png` - Distribution horaire globale (histogram)

**Qualité**:
- Résolution: 300 DPI (print quality)
- Format: PNG (lossless)
- Légendes: Titres, captions, analyses académiques
- Code couleur: Brand consistency + accessibilité

### 4. Rapport PDF Académique
**Fichier**: `Rapport_Analyse_Tweets_FreeMobile.pdf`

**Structure** (5+ pages):
- Page 1: Titre, contexte, jeu de données, méthodologie
- Page 2: Nettoyage + 5 exemples conservés + 5 rejetés avec motifs
- Page 3: KPIs clés (tableaux)
- Page 4: Visualisations (figures 1-2)
- Page 5: Visualisations (figures 3-4)
- Page 6: Interprétation et limites

---

## 🔧 Méthodologie

### Filtrage
- ✅ Suppression retweets (`is_retweet == True`)
- ✅ Suppression doublons textuels et tweet_id
- ✅ Conservation uniquement français (`lang == 'fr'`)
- ✅ Exclusion spam/humour (regex: `concours|lol|mdr`)

### Nettoyage Textuel
- Normalisation casse (minuscules)
- Suppression URLs: `r'http\S+'`
- Suppression mentions: `r'@(?!free)\w+'`
- Normalisation espaces

### Enrichissement

#### Sentiment (Lexique Français)
- **Positif**: merci, parfait, super, génial, top, résolu, satisfait
- **Négatif**: problème, bug, panne, coupure, déçu, nul, incompétent, bloqué
- **Score**: `mots_positifs - mots_negatifs`

#### Mots-Clés Dominants
- **Méthode**: TF-IDF (scikit-learn)
- **Top features**: 50
- **Extraction**: Score TF-IDF maximal par tweet

#### Classification Thématique
- **technique**: `r'\b(bug|panne|problème)\b'`
- **reseau**: `r'\b(réseau|signal|connexion)\b'`
- **facture**: `r'\b(facture|paiement|prix)\b'`
- **service_client**: `r'\b(service|sav|conseiller)\b'`

#### Détection Urgence
Regex: `r'\b(depuis \d+ jours|aucun accès|urgent|inadmissible)\b'`

---

## 📈 KPIs Calculés

| KPI | Description | Méthode |
|-----|-------------|---------|
| **Volume par jour** | Nb tweets/jour | Groupby date |
| **% Négatifs** | Tweets négatifs / total | Lexique sentiment |
| **% Neutres** | Tweets neutres / total | Lexique sentiment |
| **% Positifs** | Tweets positifs / total | Lexique sentiment |
| **Top 5 thèmes** | Thèmes principaux | Regex classification |
| **% Urgents** | Tweets urgents / total | Regex urgence |
| **Top 20 mots négatifs** | Mots-clés TF-IDF | TF-IDF sur corpus négatif |
| **Heure de pointe** | Heure max volume | Groupby hour |

---

## 🔍 Exemples de Résultats Attendus

### Distribution Sentiments Typique
- **Négatif**: 60-70% (réclamations, problèmes)
- **Neutre**: 20-30% (demandes info)
- **Positif**: 5-15% (remerciements)

### Top 3 Thèmes Fréquents
1. **Technique** (40%): bugs, pannes
2. **Réseau** (20%): couverture, signal
3. **Service Client** (15%): SAV, attente

### Tweets Urgents
- **Proportion**: 15-25%
- **Critères**: Durée (>3 jours), absence service, termes forts

---

## ⚙️ Configuration Avancée

### Modifier les Lexiques de Sentiment

**Fichier**: `scripts/part1_cleaning.py`

```python
# Ajouter mots positifs
mots_positifs = {'merci', 'parfait', 'super', 'NOUVEAU_MOT'}

# Ajouter mots négatifs
mots_negatifs = {'problème', 'bug', 'NOUVEAU_MOT'}
```

### Modifier les Regex Thématiques

**Fichier**: `scripts/part1_cleaning.py`

```python
themes_regex = {
    'technique': r'\b(bug|panne|NOUVEAU_PATTERN)\b',
    # ... autres thèmes
}
```

### Ajuster la Détection d'Urgence

```python
urgence_regex = r'\b(depuis \d+ jours|NOUVEAU_CRITERE)\b'
```

---

## 🐛 Dépannage

### Erreur: "Fichier CSV introuvable"
**Solution**: Placer `free_tweet_export.csv` dans `data/raw/`

### Erreur: "Module not found"
**Solution**: Installer les dépendances
```bash
pip install -r requirements.txt
```

### Erreur: "Colonnes manquantes"
**Solution**: Le script normalise automatiquement. Vérifier que les colonnes `text` et `created_at` existent.

### PDF vide ou incomplet
**Solution**: Vérifier que les visualisations PNG ont été générées dans `figures/`

---

## 📚 Bibliothèques Utilisées

- **pandas** (2.0+): Manipulation données
- **numpy** (1.24+): Calculs numériques
- **matplotlib** (3.7+): Visualisations de base
- **seaborn** (0.12+): Visualisations avancées
- **wordcloud** (1.9+): Nuages de mots
- **scikit-learn** (1.3+): TF-IDF, ML
- **reportlab** (4.0+): Génération PDF
- **squarify** (0.4+): Treemaps

---

## 📝 Citation Académique

```bibtex
@mastersthesis{archimede2025freemobile,
  title={Analyse Académique des Tweets du Service Client Free Mobile},
  author={Archimède, Anderson},
  year={2025},
  school={Master Data Science et Intelligence Artificielle},
  type={Mémoire de Master}
}
```

---

## 📧 Support

Pour questions ou problèmes:
- Consulter les logs d'exécution
- Vérifier la structure des données d'entrée
- Tester avec le dataset de démonstration

---

## ✅ Checklist Avant Soutenance

- [ ] Dataset `free_tweet_export.csv` placé dans `data/raw/`
- [ ] Toutes les dépendances installées
- [ ] Script exécuté sans erreur
- [ ] 5 visualisations générées dans `figures/`
- [ ] Rapport PDF généré (5+ pages)
- [ ] KPIs vérifiés et cohérents
- [ ] Code commenté et reproductible
- [ ] Présentation prête (slide deck)

---

**Bonne chance pour votre soutenance! 🎓**
