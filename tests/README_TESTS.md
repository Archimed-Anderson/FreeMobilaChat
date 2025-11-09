# 🧪 Suite de Tests - FreeMobilaChat Mistral Integration

## 📋 Vue d'Ensemble

Suite complète de tests pour validation avant production.

**Couverture:**
- ✅ Tests unitaires (prétraitement + modèles)
- ✅ Tests de performance (latence + scalabilité)
- ✅ Tests d'équité et de biais
- ✅ Tests de sécurité (injection + accès)
- ✅ Tests d'intégration (workflow complet)

**Total:** 40+ tests automatisés

---

## 🚀 Exécution des Tests

### Méthode 1: Script Automatique (Recommandé)

```bash
python tests/run_all_tests.py
```

**Ce script:**
- Exécute tous les tests
- Génère un rapport JSON
- Enregistre dans le registre des modèles
- Valide automatiquement si taux de succès ≥ 95%

---

### Méthode 2: Tests Individuels

```bash
# Tests unitaires - Prétraitement
python -m unittest tests.test_unit_preprocessing -v

# Tests unitaires - Classificateur
python -m unittest tests.test_unit_classifier -v

# Tests de performance
python -m unittest tests.test_performance -v

# Tests d'équité
python -m unittest tests.test_fairness_bias -v

# Tests de sécurité
python -m unittest tests.test_security -v

# Tests d'intégration
python -m unittest tests.test_integration -v
```

---

### Méthode 3: Avec Pytest (Si installé)

```bash
pytest tests/ -v --tb=short
```

---

## 📊 Suites de Tests Détaillées

### 1. Tests Unitaires - Prétraitement (`test_unit_preprocessing.py`)

**Classe `TestTweetCleaner`:**
- `test_remove_duplicates()` - Déduplication MD5
- `test_clean_text_urls()` - Suppression URLs
- `test_clean_text_mentions()` - Suppression mentions @
- `test_clean_text_hashtags()` - Suppression hashtags #
- `test_clean_text_emojis()` - Conversion emojis
- `test_process_dataframe()` - Pipeline complet
- `test_empty_text_handling()` - Gestion valeurs manquantes
- `test_helper_function()` - Fonction helper
- `test_batch_clean()` - Nettoyage par lot

**Classe `TestTweetCleanerEdgeCases`:**
- `test_empty_dataframe()` - DataFrame vide
- `test_missing_column()` - Colonne manquante
- `test_special_characters()` - Caractères spéciaux
- `test_very_long_tweet()` - Tweet très long (5000 char)

**Total:** 13 tests

---

### 2. Tests Unitaires - Classificateur (`test_unit_classifier.py`)

**Classe `TestMistralClassifier`:**
- `test_initialization()` - Initialisation correcte
- `test_build_prompt()` - Construction du prompt
- `test_parse_ollama_response_valid()` - Parsing JSON valide
- `test_parse_ollama_response_invalid()` - Parsing JSON invalide
- `test_fallback_classification()` - Classification fallback
- `test_classify_dataframe()` - Classification DataFrame
- `test_get_classification_stats()` - Statistiques

**Classe `TestOllamaUtilities`:**
- `test_check_ollama_availability()` - Disponibilité Ollama
- `test_list_available_models()` - Liste modèles
- `test_classify_single_tweet()` - Tweet unique

**Classe `TestCleanerConfiguration`:**
- `test_configuration_urls_only()` - Config URLs
- `test_configuration_mentions_only()` - Config mentions

**Total:** 12 tests

---

### 3. Tests de Performance (`test_performance.py`)

**Classe `TestCleaningPerformance`:**
- `test_cleaning_small_dataset()` - 500 tweets < 1s
- `test_cleaning_large_dataset()` - 5000 tweets < 5s (spec)
- `test_deduplication_performance()` - Déduplication rapide

**Classe `TestClassificationPerformance`:**
- `test_fallback_classification_speed()` - Vitesse fallback
- `test_batch_processing_scalability()` - Scalabilité
- `test_memory_usage()` - Mémoire < 1GB (spec)

**Classe `TestLatencyMeasurement`:**
- `test_response_time_single_tweet()` - Latence < 100ms
- `test_throughput_batch()` - Débit > 100 tweets/s

**Total:** 8 tests

---

### 4. Tests d'Équité et Biais (`test_fairness_bias.py`)

**Classe `TestSentimentFairness`:**
- `test_no_gender_bias()` - Pas de biais de genre
- `test_no_regional_bias()` - Pas de biais géographique
- `test_category_distribution_balance()` - Distribution équilibrée
- `test_confidence_consistency()` - Cohérence confiance

**Classe `TestBiasDetection`:**
- `test_no_price_bias()` - Pas de biais de prix
- `test_no_time_bias()` - Pas de biais temporel
- `test_balanced_positive_negative()` - Équilibre pos/neg

**Classe `TestCategorizationFairness`:**
- `test_product_category_consistency()` - Cohérence catégorie
- `test_no_category_dominance()` - Pas de dominance

**Total:** 9 tests

---

### 5. Tests de Sécurité (`test_security.py`)

**Classe `TestPromptInjection`:**
- `test_malicious_prompt_injection()` - Injection prompt
- `test_json_escaping()` - Échappement JSON
- `test_sql_injection_attempts()` - Injection SQL

**Classe `TestDataValidation`:**
- `test_input_sanitization()` - Sanitisation entrées
- `test_dataframe_column_validation()` - Validation colonnes
- `test_max_tweet_length()` - Protection DoS

**Classe `TestAccessControl`:**
- `test_no_filesystem_access()` - Pas d'accès fichiers
- `test_no_command_execution()` - Pas d'exécution commandes

**Classe `TestConfidenceScoreSecurity`:**
- `test_confidence_bounds()` - Scores dans [0, 1]
- `test_no_confidence_manipulation()` - Pas de manipulation

**Total:** 10 tests

---

### 6. Tests d'Intégration (`test_integration.py`)

**Classe `TestCompleteWorkflow`:**
- `test_end_to_end_workflow()` - Workflow complet
- `test_data_integrity_through_pipeline()` - Intégrité données
- `test_error_recovery()` - Récupération erreurs

**Classe `TestConcurrency`:**
- `test_multiple_classifications_sequential()` - Concurrent

**Classe `TestModelVersioning`:**
- `test_classification_metadata()` - Métadonnées
- `test_reproducibility()` - Reproductibilité

**Classe `TestAPIValidation`:**
- `test_classifier_stats_format()` - Format API

**Total:** 7 tests

---

## 📈 Total: 59 Tests Automatisés

| Suite | Tests | Focus |
|-------|-------|-------|
| Unit Preprocessing | 13 | Nettoyage données |
| Unit Classifier | 12 | Classification |
| Performance | 8 | Latence + scalabilité |
| Fairness & Bias | 9 | Équité + biais |
| Security | 10 | Sécurité + injection |
| Integration | 7 | Workflow end-to-end |

---

## ✅ Critères de Validation

### Pour Déploiement en Production

Un modèle est validé pour production SI:

- ✅ **Taux de succès ≥ 95%** (au moins 56/59 tests passés)
- ✅ **0 erreur de sécurité** (tous les tests de sécurité passés)
- ✅ **Performance conforme specs**:
  - Nettoyage 5000 tweets < 5s
  - Mémoire < 1GB
  - Throughput ≥ 10 tweets/s
- ✅ **0 biais critique détecté**
- ✅ **Métadonnées complètes** (versioning, timestamp)

---

## 📊 Rapports Générés

### Après exécution, les fichiers suivants sont créés :

1. **`tests/test_report.json`**
   - Résultats détaillés en JSON
   - Timestamp, métriques, détails

2. **`tests/model_versions.json`**
   - Registre de toutes les versions
   - Historique des validations

3. **`tests/model_registry_report.md`**
   - Rapport lisible du registre
   - Toutes les versions documentées

---

## 🔍 Interprétation des Résultats

### Sortie Attendue (Succès)

```
🧪 SUITE DE TESTS COMPLÈTE - VALIDATION AVANT PRODUCTION

✅ Module chargé: test_unit_preprocessing
✅ Module chargé: test_unit_classifier
✅ Module chargé: test_performance
✅ Module chargé: test_fairness_bias
✅ Module chargé: test_security
✅ Module chargé: test_integration

📊 Total de tests à exécuter: 59

[... Exécution de chaque test ...]

══════════════════════════════════════════════════════════
  📊 RÉSUMÉ DES TESTS
══════════════════════════════════════════════════════════

  Total de tests exécutés: 59
  ✅ Passés: 56
  ❌ Échecs: 2
  ⚠️ Erreurs: 1
  📈 Taux de succès: 94.9%
  ⏱️ Temps d'exécution: 3.45s

══════════════════════════════════════════════════════════
  ✅ VALIDATION RÉUSSIE - Modèle prêt pour déploiement
══════════════════════════════════════════════════════════

📄 Rapport sauvegardé: tests/test_report.json
✅ Modèle 1.0.0 enregistré et validé automatiquement
📄 Registre mis à jour: tests/model_versions.json
📄 Rapport généré: tests/model_registry_report.md
```

---

## 🐛 Si Tests Échouent

### Analyser les Échecs

```bash
# Relancer avec plus de détails
python -m unittest tests.test_[nom_module] -v
```

### Échecs Communs

**`test_cleaning_large_dataset` échoue:**
- Cause: Machine trop lente
- Solution: Acceptable si < 10s

**`test_check_ollama_availability` échoue:**
- Cause: Ollama non démarré
- Solution: Démarrer Ollama (`ollama serve`)

**Tests sécurité échouent:**
- Cause: Vulnérabilité détectée
- Solution: Corriger avant déploiement

---

## 📝 Notes Importantes

### Tests Requis Avant Déploiement

1. **Tests unitaires:** OBLIGATOIRES (tous doivent passer)
2. **Tests sécurité:** OBLIGATOIRES (tous doivent passer)
3. **Tests performance:** RECOMMANDÉS (conforme specs)
4. **Tests fairness:** RECOMMANDÉS (0 biais critique)
5. **Tests intégration:** OBLIGATOIRES (workflow OK)

### Maintenance

- Exécuter les tests avant chaque déploiement
- Mettre à jour le registre après chaque modification
- Documenter toute régression détectée

---

**Pour lancer les tests maintenant:**

```bash
python tests/run_all_tests.py
```

---

**Date:** 2024-11-07  
**Version:** 1.0  
**Total Tests:** 59  
**Couverture:** Prétraitement, Classification, Performance, Équité, Sécurité, Intégration  

