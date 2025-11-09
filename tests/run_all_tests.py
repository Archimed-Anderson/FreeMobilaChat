"""
Script d'Exécution de Tous les Tests - Suite Complète
======================================================

Exécute tous les tests (unit, performance, fairness, security) et génère un rapport.
"""

import unittest
import sys
import os
import time
from datetime import datetime

# Ajout du chemin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_test_suite():
    """Exécute la suite complète de tests"""
    
    print("\n" + "="*100)
    print("🧪 SUITE DE TESTS COMPLÈTE - VALIDATION AVANT PRODUCTION")
    print("="*100 + "\n")
    
    # Découverte des tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Exécution avec rapport détaillé
    runner = unittest.TextTestRunner(verbosity=2)
    
    start_time = time.time()
    result = runner.run(suite)
    elapsed_time = time.time() - start_time
    
    # Compilation des résultats
    print("\n" + "="*100)
    print("📊 RÉSULTATS DE LA VALIDATION")
    print("="*100)
    print(f"\n⏱️  Temps total: {elapsed_time:.2f} secondes")
    print(f"📝 Tests exécutés: {result.testsRun}")
    print(f"✅ Réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Échecs: {len(result.failures)}")
    print(f"⚠️  Erreurs: {len(result.errors)}")
    print(f"⏭️  Ignorés: {len(result.skipped)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"📈 Taux de succès: {success_rate:.1f}%")
    
    # Statut final
    print("\n" + "="*100)
    if result.wasSuccessful():
        print("✅ VALIDATION RÉUSSIE - PRÊT POUR PRODUCTION")
    else:
        print("❌ VALIDATION ÉCHOUÉE - CORRECTIONS REQUISES")
    print("="*100 + "\n")
    
    # Retourner les résultats pour enregistrement
    return {
        'timestamp': datetime.now().isoformat(),
        'total_tests': result.testsRun,
        'passed': result.testsRun - len(result.failures) - len(result.errors),
        'failed': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped),
        'success_rate': success_rate,
        'elapsed_time': elapsed_time,
        'status': 'PASSED' if result.wasSuccessful() else 'FAILED'
    }


if __name__ == '__main__':
    results = run_test_suite()
    
    # Sauvegarder les résultats
    import json
    
    report_file = f"tests/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Rapport sauvegardé: {report_file}\n")
    
    # Exit code selon résultat
    sys.exit(0 if results['status'] == 'PASSED' else 1)
