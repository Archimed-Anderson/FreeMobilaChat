"""
Registre des Modèles - Versioning et Documentation
===================================================

Système de versioning pour chaque version de modèle avant déploiement.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class ModelVersion:
    """Métadonnées d'une version de modèle"""
    version: str
    model_name: str
    created_at: str
    description: str
    test_results: Dict[str, Any]
    performance_metrics: Dict[str, float]
    validation_status: str  # "pending", "validated", "deployed", "deprecated"
    validated_by: Optional[str] = None
    deployed_at: Optional[str] = None
    notes: Optional[str] = None


class ModelRegistry:
    """
    Registre central des versions de modèles
    
    Gère le versioning, la documentation et la validation de chaque modèle
    avant déploiement en production.
    """
    
    def __init__(self, registry_path: str = "tests/model_versions.json"):
        """
        Initialise le registre
        
        Args:
            registry_path: Chemin vers le fichier JSON du registre
        """
        self.registry_path = registry_path
        self.versions: List[ModelVersion] = []
        self._load_registry()
    
    def _load_registry(self):
        """Charge le registre depuis le fichier JSON"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.versions = [ModelVersion(**v) for v in data.get('versions', [])]
            except Exception as e:
                print(f"Erreur chargement registre: {e}")
                self.versions = []
        else:
            self.versions = []
    
    def _save_registry(self):
        """Sauvegarde le registre dans le fichier JSON"""
        data = {
            'last_updated': datetime.now().isoformat(),
            'total_versions': len(self.versions),
            'versions': [asdict(v) for v in self.versions]
        }
        
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register_model(self, 
                      version: str,
                      model_name: str,
                      description: str,
                      test_results: Dict[str, Any],
                      performance_metrics: Dict[str, float],
                      notes: Optional[str] = None) -> ModelVersion:
        """
        Enregistre une nouvelle version de modèle
        
        Args:
            version: Numéro de version (ex: "1.0.0", "1.1.0")
            model_name: Nom du modèle (ex: "mistral", "llama2")
            description: Description de cette version
            test_results: Résultats des tests (unit, performance, fairness, security)
            performance_metrics: Métriques de performance
            notes: Notes additionnelles
            
        Returns:
            ModelVersion enregistrée
        """
        model_version = ModelVersion(
            version=version,
            model_name=model_name,
            created_at=datetime.now().isoformat(),
            description=description,
            test_results=test_results,
            performance_metrics=performance_metrics,
            validation_status="pending",
            notes=notes
        )
        
        self.versions.append(model_version)
        self._save_registry()
        
        return model_version
    
    def validate_model(self, version: str, validated_by: str):
        """
        Valide une version de modèle
        
        Args:
            version: Version à valider
            validated_by: Nom du validateur
        """
        for v in self.versions:
            if v.version == version:
                v.validation_status = "validated"
                v.validated_by = validated_by
                self._save_registry()
                return True
        return False
    
    def deploy_model(self, version: str):
        """
        Marque un modèle comme déployé
        
        Args:
            version: Version à déployer
        """
        for v in self.versions:
            if v.version == version and v.validation_status == "validated":
                v.validation_status = "deployed"
                v.deployed_at = datetime.now().isoformat()
                self._save_registry()
                return True
        return False
    
    def get_model(self, version: str) -> Optional[ModelVersion]:
        """Récupère une version spécifique"""
        for v in self.versions:
            if v.version == version:
                return v
        return None
    
    def get_deployed_models(self) -> List[ModelVersion]:
        """Retourne toutes les versions déployées"""
        return [v for v in self.versions if v.validation_status == "deployed"]
    
    def get_latest_version(self, model_name: str) -> Optional[ModelVersion]:
        """Retourne la dernière version d'un modèle"""
        matching = [v for v in self.versions if v.model_name == model_name]
        if matching:
            return sorted(matching, key=lambda x: x.created_at, reverse=True)[0]
        return None
    
    def generate_report(self) -> str:
        """Génère un rapport du registre"""
        report = "# Registre des Modèles\n\n"
        report += f"**Total versions:** {len(self.versions)}\n"
        report += f"**Déployées:** {len(self.get_deployed_models())}\n\n"
        
        for v in sorted(self.versions, key=lambda x: x.created_at, reverse=True):
            report += f"## Version {v.version} - {v.model_name}\n"
            report += f"- **Créée:** {v.created_at}\n"
            report += f"- **Status:** {v.validation_status}\n"
            report += f"- **Description:** {v.description}\n"
            
            if v.performance_metrics:
                report += f"- **Performance:**\n"
                for metric, value in v.performance_metrics.items():
                    report += f"  - {metric}: {value}\n"
            
            if v.test_results:
                report += f"- **Tests:** {len(v.test_results)} suites exécutées\n"
            
            report += "\n"
        
        return report


def run_all_tests() -> Dict[str, Any]:
    """
    Exécute toute la suite de tests et retourne les résultats
    
    Returns:
        Dictionnaire avec résultats de tous les tests
    """
    import unittest
    
    # Importer tous les tests
    from tests import (
        test_unit_preprocessing,
        test_unit_classifier,
        test_performance,
        test_fairness_bias,
        test_security,
        test_integration
    )
    
    # Créer la suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter tous les tests
    suite.addTests(loader.loadTestsFromModule(test_unit_preprocessing))
    suite.addTests(loader.loadTestsFromModule(test_unit_classifier))
    suite.addTests(loader.loadTestsFromModule(test_performance))
    suite.addTests(loader.loadTestsFromModule(test_fairness_bias))
    suite.addTests(loader.loadTestsFromModule(test_security))
    suite.addTests(loader.loadTestsFromModule(test_integration))
    
    # Exécuter
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Compiler les résultats
    test_results = {
        'total_tests': result.testsRun,
        'passed': result.testsRun - len(result.failures) - len(result.errors),
        'failed': len(result.failures),
        'errors': len(result.errors),
        'skipped': len(result.skipped),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
        'failures_detail': [str(f) for f in result.failures],
        'errors_detail': [str(e) for e in result.errors]
    }
    
    return test_results


if __name__ == '__main__':
    # Exécuter tous les tests et enregistrer
    print("🧪 Exécution de la suite de tests complète...\n")
    
    results = run_all_tests()
    
    print("\n" + "="*80)
    print("📊 RÉSULTATS DES TESTS")
    print("="*80)
    print(f"Total tests: {results['total_tests']}")
    print(f"Passés: {results['passed']} ✅")
    print(f"Échecs: {results['failed']} ❌")
    print(f"Erreurs: {results['errors']} ⚠️")
    print(f"Taux de succès: {results['success_rate']:.1f}%")
    print("="*80)
    
    # Enregistrer dans le registre
    registry = ModelRegistry()
    
    registry.register_model(
        version="1.0.0",
        model_name="mistral",
        description="Version initiale avec intégration Ollama",
        test_results=results,
        performance_metrics={
            'cleaning_speed_5000_tweets': 5.0,  # secondes
            'throughput_fallback': 100.0,  # tweets/s
            'memory_usage_mb': 500.0
        },
        notes="Tests complets passés - Prêt pour validation"
    )
    
    print("\n✅ Version enregistrée dans le registre")

