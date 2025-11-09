"""
🐛 ÉTAPE 4: SESSION DE BUG BASH
================================
Exécution systématique des tests et documentation des problèmes

Tests effectués:
- Exécution de tous les scénarios de test
- Détection des bugs et problèmes
- Documentation complète des issues
- Génération d'un rapport de bug bash

Date: 2025-11-08
"""

import sys
import os
sys.path.insert(0, 'streamlit_app')

import pandas as pd
import numpy as np
import pickle
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

print("\n" + "╔" + "="*78 + "╗")
print("║" + " "*25 + "🐛 ÉTAPE 4: BUG BASH SESSION" + " "*24 + "║")
print("║" + " "*20 + "Tests Systématiques et Documentation" + " "*19 + "║")
print("╚" + "="*78 + "╝\n")

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    'models_dir': 'models/baseline',
    'test_scenarios_file': 'tests/scenarios/test_scenarios.json',
    'test_cases_file': 'tests/scenarios/test_cases.json',
    'validation_file': 'data/training/validation_dataset.csv',
    'test_file': 'data/training/test_dataset_split.csv',
    'output_dir': 'tests/bug_bash_results'
}

os.makedirs(CONFIG['output_dir'], exist_ok=True)

print("⚙️  CONFIGURATION:")
print(f"   • Modèles: {CONFIG['models_dir']}/")
print(f"   • Scénarios: {CONFIG['test_scenarios_file']}")
print(f"   • Résultats: {CONFIG['output_dir']}/\n")

# ============================================================================
# PHASE 1: CHARGEMENT DES MODÈLES
# ============================================================================
print("📦 [1/6] Chargement des modèles...")

try:
    with open(os.path.join(CONFIG['models_dir'], 'vectorizer_model.pkl'), 'rb') as f:
        vectorizer = pickle.load(f)
    with open(os.path.join(CONFIG['models_dir'], 'sentiment_model.pkl'), 'rb') as f:
        model_sentiment = pickle.load(f)
    with open(os.path.join(CONFIG['models_dir'], 'categorie_model.pkl'), 'rb') as f:
        model_categorie = pickle.load(f)
    with open(os.path.join(CONFIG['models_dir'], 'priority_model.pkl'), 'rb') as f:
        model_priority = pickle.load(f)
    
    print("   ✅ Tous les modèles chargés avec succès\n")
except Exception as e:
    print(f"   ❌ ERREUR lors du chargement: {e}\n")
    sys.exit(1)

# ============================================================================
# PHASE 2: CHARGEMENT DES SCÉNARIOS ET CAS DE TEST
# ============================================================================
print("📋 [2/6] Chargement des scénarios et cas de test...")

with open(CONFIG['test_scenarios_file'], 'r', encoding='utf-8') as f:
    test_scenarios = json.load(f)

with open(CONFIG['test_cases_file'], 'r', encoding='utf-8') as f:
    test_cases = json.load(f)

print(f"   ✅ {len(test_scenarios)} scénarios chargés")
print(f"   ✅ {sum(len(cases) for cases in test_cases.values())} cas de test chargés\n")

# ============================================================================
# PHASE 3: EXÉCUTION DES TESTS ET DÉTECTION DE BUGS
# ============================================================================
print("🧪 [3/6] Exécution des tests et détection de bugs...\n")

bugs_found = []
issues_found = []
warnings_found = []
test_results = {}

def predict_tweet(text):
    """Prédiction pour un tweet donné"""
    try:
        if not text or text.strip() == '':
            return {
                'sentiment': 'neutre',
                'categorie': 'autre',
                'priority': 'basse',
                'error': None
            }
        
        X = vectorizer.transform([text])
        
        return {
            'sentiment': model_sentiment.predict(X)[0],
            'categorie': model_categorie.predict(X)[0],
            'priority': model_priority.predict(X)[0],
            'error': None
        }
    except Exception as e:
        return {
            'sentiment': None,
            'categorie': None,
            'priority': None,
            'error': str(e)
        }

# TEST 1: Edge Cases - Texte Vide
print("   [TEST 1/6] Edge Cases - Texte Vide...")
for case in test_cases['edge_case_empty_texts']:
    result = predict_tweet(case['text'])
    
    if result['error']:
        bugs_found.append({
            'id': f"BUG-{len(bugs_found)+1:03d}",
            'severity': 'HIGH',
            'category': 'edge_case',
            'test_case': case['id'],
            'description': f"Erreur avec texte vide: {result['error']}",
            'input': case['text'],
            'expected': 'default_prediction',
            'actual': 'error',
            'stack_trace': result['error']
        })
    elif result['sentiment'] is None:
        issues_found.append({
            'id': f"ISSUE-{len(issues_found)+1:03d}",
            'severity': 'MEDIUM',
            'category': 'edge_case',
            'test_case': case['id'],
            'description': f"Prédiction None pour texte vide",
            'input': case['text']
        })

print(f"      ✅ Testé: {len(test_cases['edge_case_empty_texts'])} cas")
print(f"      🐛 Bugs trouvés: {len([b for b in bugs_found if 'empty' in b.get('test_case', '').lower()])}")

# TEST 2: Edge Cases - Caractères Spéciaux
print("   [TEST 2/6] Edge Cases - Caractères Spéciaux...")
for case in test_cases['edge_case_special_characters']:
    result = predict_tweet(case['text'])
    
    if result['error']:
        bugs_found.append({
            'id': f"BUG-{len(bugs_found)+1:03d}",
            'severity': 'HIGH',
            'category': 'special_characters',
            'test_case': case['id'],
            'description': f"Erreur avec caractères spéciaux: {result['error']}",
            'input': case['text']
        })

print(f"      ✅ Testé: {len(test_cases['edge_case_special_characters'])} cas")

# TEST 3: Boundary Cases - Ambiguïté
print("   [TEST 3/6] Boundary Cases - Ambiguïté...")
ambiguity_issues = 0
for case in test_cases['boundary_case_ambiguous']:
    result = predict_tweet(case['text'])
    
    # Vérifier si les prédictions sont cohérentes pour du texte ambigu
    if result['sentiment'] == 'positif' and 'problème' in case['text'].lower():
        warnings_found.append({
            'id': f"WARN-{len(warnings_found)+1:03d}",
            'severity': 'LOW',
            'category': 'ambiguity',
            'test_case': case['id'],
            'description': f"Sentiment positif détecté avec mot négatif",
            'input': case['text'],
            'prediction': result
        })
        ambiguity_issues += 1

print(f"      ✅ Testé: {len(test_cases['boundary_case_ambiguous'])} cas")
print(f"      ⚠️  Warnings: {ambiguity_issues}")

# TEST 4: Critical Cases - Urgence
print("   [TEST 4/6] Critical Cases - Urgence...")
urgent_misses = 0
for case in test_cases['critical_case_urgent']:
    result = predict_tweet(case['text'])
    
    if result['priority'] != 'haute' and case.get('expected_priority') == 'haute':
        issues_found.append({
            'id': f"ISSUE-{len(issues_found)+1:03d}",
            'severity': 'CRITICAL',
            'category': 'urgent_detection',
            'test_case': case['id'],
            'description': f"Tweet urgent non détecté comme priorité haute",
            'input': case['text'],
            'expected': 'haute',
            'actual': result['priority']
        })
        urgent_misses += 1

print(f"      ✅ Testé: {len(test_cases['critical_case_urgent'])} cas")
print(f"      ❌ Misses: {urgent_misses}")

# TEST 5: Performance - Vitesse
print("   [TEST 5/6] Performance - Vitesse...")
start_time = time.time()
test_texts = ["test"] * 100
for text in test_texts:
    _ = predict_tweet(text)
elapsed = time.time() - start_time
avg_time_ms = (elapsed / len(test_texts)) * 1000

print(f"      ✅ 100 prédictions en {elapsed:.2f}s")
print(f"      ⏱️  Temps moyen: {avg_time_ms:.2f}ms par tweet")

if avg_time_ms > 100:
    warnings_found.append({
        'id': f"WARN-{len(warnings_found)+1:03d}",
        'severity': 'MEDIUM',
        'category': 'performance',
        'description': f"Temps d'inférence élevé: {avg_time_ms:.2f}ms (seuil: 100ms)",
        'threshold': 100,
        'actual': avg_time_ms
    })

# TEST 6: Consistency
print("   [TEST 6/6] Consistency - Répétabilité...")
test_text = "problème de connexion internet"
predictions = []
for _ in range(10):
    result = predict_tweet(test_text)
    predictions.append((result['sentiment'], result['categorie'], result['priority']))

unique_predictions = len(set(predictions))
print(f"      ✅ 10 prédictions effectuées")
print(f"      🔄 Prédictions uniques: {unique_predictions}")

if unique_predictions > 1:
    bugs_found.append({
        'id': f"BUG-{len(bugs_found)+1:03d}",
        'severity': 'HIGH',
        'category': 'consistency',
        'description': f"Prédictions inconsistantes pour le même input ({unique_predictions} variations)",
        'input': test_text,
        'predictions': [str(p) for p in set(predictions)]
    })

print()

# ============================================================================
# PHASE 4: ANALYSE DES RÉSULTATS
# ============================================================================
print("📊 [4/6] Analyse des résultats...\n")

print(f"   🐛 BUGS CRITIQUES: {len([b for b in bugs_found if b['severity'] == 'HIGH'])}")
print(f"   ⚠️  ISSUES: {len([i for i in issues_found if i['severity'] in ['CRITICAL', 'HIGH']])}")
print(f"   💡 WARNINGS: {len(warnings_found)}")
print(f"\n   Total de problèmes identifiés: {len(bugs_found) + len(issues_found) + len(warnings_found)}\n")

# ============================================================================
# PHASE 5: SAUVEGARDE DES RÉSULTATS
# ============================================================================
print("💾 [5/6] Sauvegarde des résultats...")

# Rapport de bug bash
bug_bash_report = {
    'metadata': {
        'date': datetime.now().isoformat(),
        'duration_minutes': 'Exécution automatisée',
        'tester': 'Automated Bug Bash Script',
        'models_tested': [
            'vectorizer',
            'sentiment_classifier',
            'categorie_classifier',
            'priority_classifier'
        ]
    },
    'summary': {
        'total_tests_run': 6,
        'bugs_found': len(bugs_found),
        'issues_found': len(issues_found),
        'warnings_found': len(warnings_found),
        'critical_issues': len([i for i in issues_found if i['severity'] == 'CRITICAL']),
        'high_priority_bugs': len([b for b in bugs_found if b['severity'] == 'HIGH'])
    },
    'bugs': bugs_found,
    'issues': issues_found,
    'warnings': warnings_found,
    'performance_metrics': {
        'average_inference_time_ms': round(avg_time_ms, 2),
        'throughput_tweets_per_second': round(1000 / avg_time_ms, 2) if avg_time_ms > 0 else 0
    }
}

report_file = os.path.join(CONFIG['output_dir'], f'bug_bash_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(bug_bash_report, f, indent=2, ensure_ascii=False)

print(f"   ✅ Rapport sauvegardé: {report_file}\n")

# ============================================================================
# PHASE 6: GÉNÉRATION DU RAPPORT LISIBLE
# ============================================================================
print("📄 [6/6] Génération du rapport lisible...\n")

# Rapport markdown
markdown_report = f"""# 🐛 Bug Bash Report - FreeMobilaChat
## Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Résumé Exécutif

| Métrique | Valeur |
|----------|--------|
| **Tests exécutés** | {bug_bash_report['summary']['total_tests_run']} |
| **Bugs trouvés** | {bug_bash_report['summary']['bugs_found']} |
| **Issues identifiées** | {bug_bash_report['summary']['issues_found']} |
| **Warnings** | {bug_bash_report['summary']['warnings_found']} |
| **Issues critiques** | {bug_bash_report['summary']['critical_issues']} |
| **Bugs haute priorité** | {bug_bash_report['summary']['high_priority_bugs']} |

**Statut Global**: {"🔴 CRITIQUE" if bug_bash_report['summary']['critical_issues'] > 0 else "🟠 À SURVEILLER" if bug_bash_report['summary']['bugs_found'] > 0 else "🟢 BON"}

---

## 🐛 Bugs Identifiés ({len(bugs_found)})

"""

for bug in bugs_found:
    markdown_report += f"""
### {bug['id']} - {bug['severity']}
- **Catégorie**: {bug['category']}
- **Description**: {bug['description']}
- **Test Case**: {bug.get('test_case', 'N/A')}
- **Input**: `{bug.get('input', 'N/A')}`
- **Expected**: {bug.get('expected', 'N/A')}
- **Actual**: {bug.get('actual', 'N/A')}

"""

markdown_report += f"""
---

## ⚠️  Issues Identifiées ({len(issues_found)})

"""

for issue in issues_found:
    markdown_report += f"""
### {issue['id']} - {issue['severity']}
- **Catégorie**: {issue['category']}
- **Description**: {issue['description']}
- **Input**: `{issue.get('input', 'N/A')}`

"""

markdown_report += f"""
---

## 💡 Warnings ({len(warnings_found)})

"""

for warn in warnings_found:
    markdown_report += f"""
### {warn['id']} - {warn['severity']}
- **Catégorie**: {warn['category']}
- **Description**: {warn['description']}

"""

markdown_report += f"""
---

## 🎯 Performance

- **Temps moyen d'inférence**: {avg_time_ms:.2f}ms
- **Throughput**: {1000/avg_time_ms:.2f} tweets/seconde
- **Seuil acceptable**: 100ms
- **Statut**: {"✅ BON" if avg_time_ms < 100 else "⚠️  AMÉLIORATION NÉCESSAIRE"}

---

## 📝 Recommandations

"""

if bug_bash_report['summary']['critical_issues'] > 0:
    markdown_report += "1. **URGENT**: Corriger les {0} issues critiques avant le déploiement\n".format(bug_bash_report['summary']['critical_issues'])

if bug_bash_report['summary']['high_priority_bugs'] > 0:
    markdown_report += "2. **HIGH**: Corriger les {0} bugs haute priorité\n".format(bug_bash_report['summary']['high_priority_bugs'])

if avg_time_ms > 100:
    markdown_report += "3. **PERFORMANCE**: Optimiser le temps d'inférence (actuel: {0:.2f}ms, cible: <100ms)\n".format(avg_time_ms)

if len(warnings_found) > 0:
    markdown_report += "4. **QUALITY**: Investiguer les {0} warnings pour améliorer la qualité\n".format(len(warnings_found))

markdown_report += """
---

*Rapport généré automatiquement par le script de Bug Bash*
"""

markdown_file = os.path.join(CONFIG['output_dir'], f'bug_bash_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
with open(markdown_file, 'w', encoding='utf-8') as f:
    f.write(markdown_report)

print(f"   ✅ Rapport markdown sauvegardé: {markdown_file}\n")

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================
print("╔" + "="*78 + "╗")
print("║" + " "*25 + "✅ BUG BASH COMPLÉTÉ!" + " "*27 + "║")
print("╚" + "="*78 + "╝\n")

print("📊 RÉSULTATS FINAUX:\n")
print(f"   Tests Exécutés:        {bug_bash_report['summary']['total_tests_run']}")
print(f"   Bugs Trouvés:          {bug_bash_report['summary']['bugs_found']}")
print(f"   Issues Identifiées:    {bug_bash_report['summary']['issues_found']}")
print(f"   Warnings:              {bug_bash_report['summary']['warnings_found']}")
print(f"\n   Issues Critiques:      {bug_bash_report['summary']['critical_issues']}")
print(f"   Bugs Haute Priorité:   {bug_bash_report['summary']['high_priority_bugs']}")

print(f"\n📁 RAPPORTS GÉNÉRÉS:")
print(f"   • {report_file}")
print(f"   • {markdown_file}")

print(f"\n🎯 STATUT:")
if bug_bash_report['summary']['critical_issues'] > 0:
    print("   🔴 CRITIQUE - Corrections urgentes requises")
elif bug_bash_report['summary']['high_priority_bugs'] > 0:
    print("   🟠 ATTENTION - Bugs importants à corriger")
else:
    print("   🟢 BON - Modèle fonctionnel avec warnings mineurs")

print("\n" + "="*80)
print("  🎉 ÉTAPE 4 COMPLÉTÉE AVEC SUCCÈS!")
print("="*80 + "\n")

print("📖 PROCHAINE ÉTAPE:")
print("   → Étape 5: Fine-tuner BERT pour améliorer la précision\n")

