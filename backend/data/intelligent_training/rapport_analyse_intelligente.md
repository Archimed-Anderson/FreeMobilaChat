# Rapport d'Analyse Intelligente - FreeMobilaChat

**Date**: 2025-10-22 23:15:41
**Fichier**: free_tweet_export
**Mode**: Fallback (Classification par règles)

---

## 1. Vue d'Ensemble

- **Nombre de lignes**: 100
- **Nombre de colonnes**: 6
- **Score de qualité global**: 50/100

## 2. Résumé Exécutif

Analyse automatique des tweets Free Mobile avec classification par règles.
Dataset traité avec succès en mode fallback.

## 3. Résultats de Classification

- **Tweets classifiés**: 100
- **Réclamations détectées**: 24 (24.0%)
- **Confiance moyenne**: 0.60

### Distribution des Thèmes

- AUTRE: 50
- FIBRE: 41
- MOBILE: 3
- RESEAU: 2
- TV: 2
- FACTURE: 1
- SAV: 1

### Distribution des Sentiments

- NEUTRE: 75
- NEGATIF: 13
- POSITIF: 12

## 4. Exemples de Classification

### Exemples de Réclamations
- **Tweet**: bonsoir, j'ai toujours des gros problèmes avec les services télé sur ma freebox. la panne se poursui...
  - Thème: FIBRE, Sentiment: NEGATIF, Urgence: MOYENNE
  - Justification: Classification automatique par règles (fallback)

- **Tweet**: depuis que je suis chez j’ai tellement de bug putain les coupures de tv et internet c’est hallucinan...
  - Thème: FIBRE, Sentiment: NEGATIF, Urgence: MOYENNE
  - Justification: Classification automatique par règles (fallback)

- **Tweet**: étant donné qu'après presque 2 mois sans internet toujours rien n'est fait je me demandais qui est c...
  - Thème: FIBRE, Sentiment: POSITIF, Urgence: MOYENNE
  - Justification: Classification automatique par règles (fallback)

### Exemples de Tweets Informatifs
- **Tweet**: salut , 10 coupures de fibre depuis le début de l'année, dont 2 en 3 jours ! c'est inacceptable. j'a...
  - Thème: FIBRE, Sentiment: NEUTRE

- **Tweet**: on fait comment pour vous joindre qd on est plus client?? le code barre de retour colis n est pas ac...
  - Thème: AUTRE, Sentiment: NEUTRE


## 5. Statistiques Finales

- **Total de tweets**: 100
- **Réclamations**: 24 (24.0%)
- **Sentiment Négatif**: 13
- **Sentiment Neutre**: 75
- **Sentiment Positif**: 12

## 6. Recommandations

1. Le mode fallback fonctionne correctement
2. Pour une meilleure précision, configurez une clé API OpenAI/Anthropic
3. Les résultats sont cohérents avec les règles définies

---

*Rapport généré automatiquement par le pipeline d'analyse intelligente simplifié*
