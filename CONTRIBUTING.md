# Guide de Contribution

## Contexte Académique

Ce projet a été développé dans le cadre d'un mémoire de master en Data Science. Bien qu'il soit maintenant open source, il conserve une vocation académique et pédagogique.

## Comment Contribuer

### Rapporter un Bug

Si vous identifiez un bug, veuillez créer une issue incluant :
- Description détaillée du problème
- Étapes pour reproduire le bug
- Comportement attendu vs comportement observé
- Captures d'écran si pertinent
- Environnement (OS, version Python, etc.)

### Proposer une Fonctionnalité

Pour proposer une nouvelle fonctionnalité :
1. Vérifiez qu'elle n'existe pas déjà dans les issues
2. Créez une issue détaillant :
   - Le besoin identifié
   - La solution proposée
   - Les impacts potentiels sur l'architecture existante

### Soumettre une Pull Request

1. Forkez le repository
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Standards de Code

- Respectez les conventions PEP 8 pour Python
- Ajoutez des docstrings pour toutes les fonctions
- Incluez des tests pour les nouvelles fonctionnalités
- Commentez le code de manière claire et concise
- Évitez les dépendances externes non nécessaires

### Tests

Avant de soumettre :
```bash
# Tests unitaires backend
cd backend
pytest

# Vérification du code
flake8 .
black --check .
```

## Questions

Pour toute question, n'hésitez pas à ouvrir une discussion dans l'onglet "Discussions" du repository.

## Code de Conduite

Ce projet adhère aux principes de respect, d'inclusion et de collaboration constructive. Tout comportement inapproprié sera signalé et traité conformément aux standards académiques.

