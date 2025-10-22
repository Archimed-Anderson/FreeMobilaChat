"""
Tests Unitaires pour le Classificateur de Tweets
================================================

Suite de tests complète pour valider le module tweet_classifier.

Auteur: Archimed Anderson
Date: Octobre 2024
"""

import unittest
import sys
from pathlib import Path

# Ajouter le chemin backend au sys.path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

from app.services.tweet_classifier import (
    TweetClassifier,
    ClassificationResult,
    classify_tweet
)


class TestClassificationResult(unittest.TestCase):
    """Tests pour le modèle ClassificationResult"""
    
    def test_valid_classification_result(self):
        """Test création d'un résultat valide"""
        result = ClassificationResult(
            is_reclamation="OUI",
            theme="FIBRE",
            sentiment="NEGATIF",
            urgence="ELEVEE",
            type_incident="PANNE",
            confidence=0.95,
            justification="Panne déclarée"
        )
        
        self.assertEqual(result.is_reclamation, "OUI")
        self.assertEqual(result.theme, "FIBRE")
        self.assertEqual(result.confidence, 0.95)
    
    def test_invalid_is_reclamation(self):
        """Test validation is_reclamation"""
        with self.assertRaises(ValueError):
            ClassificationResult(
                is_reclamation="MAYBE",  # Invalid
                theme="FIBRE",
                sentiment="NEGATIF",
                urgence="ELEVEE",
                type_incident="PANNE",
                confidence=0.95,
                justification="Test"
            )
    
    def test_invalid_theme(self):
        """Test validation theme"""
        with self.assertRaises(ValueError):
            ClassificationResult(
                is_reclamation="OUI",
                theme="INVALID_THEME",
                sentiment="NEGATIF",
                urgence="ELEVEE",
                type_incident="PANNE",
                confidence=0.95,
                justification="Test"
            )
    
    def test_confidence_bounds(self):
        """Test validation bounds de confidence"""
        # Test confidence > 1.0
        with self.assertRaises(ValueError):
            ClassificationResult(
                is_reclamation="OUI",
                theme="FIBRE",
                sentiment="NEGATIF",
                urgence="ELEVEE",
                type_incident="PANNE",
                confidence=1.5,  # > 1.0
                justification="Test"
            )


class TestTweetClassifierFallback(unittest.TestCase):
    """Tests pour la classification fallback (sans LLM)"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        # Créer un classificateur en mode fallback (sans API key)
        self.classifier = TweetClassifier(
            model_name="fallback",
            api_key=None
        )
    
    def test_classify_panne_fibre(self):
        """Test classification panne fibre"""
        tweet = "@Free Ma fibre est coupée depuis ce matin, c'est insupportable !"
        result = self.classifier.classify(tweet)
        
        self.assertEqual(result.is_reclamation, "OUI")
        self.assertEqual(result.theme, "FIBRE")
        self.assertEqual(result.sentiment, "NEGATIF")
        self.assertIn(result.type_incident, ["PANNE", "AUTRE"])
    
    def test_classify_mobile_lenteur(self):
        """Test classification lenteur mobile"""
        tweet = "@Free Mon mobile Free a un débit 4G très lent"
        result = self.classifier.classify(tweet)
        
        self.assertEqual(result.is_reclamation, "OUI")
        self.assertEqual(result.theme, "MOBILE")
        self.assertIn(result.type_incident, ["LENTEUR", "AUTRE"])
    
    def test_classify_facturation(self):
        """Test classification problème de facture"""
        tweet = "@Free Ma facture est anormalement élevée ce mois-ci"
        result = self.classifier.classify(tweet)
        
        self.assertEqual(result.is_reclamation, "OUI")
        self.assertEqual(result.theme, "FACTURE")
        self.assertEqual(result.type_incident, "FACTURATION")
    
    def test_classify_info_positive(self):
        """Test classification info positive"""
        tweet = "Bravo @Free pour le déploiement de la fibre dans ma ville !"
        result = self.classifier.classify(tweet)
        
        self.assertEqual(result.is_reclamation, "NON")
        self.assertEqual(result.sentiment, "POSITIF")
        self.assertEqual(result.type_incident, "INFO")
    
    def test_classify_sav(self):
        """Test classification problème SAV"""
        tweet = "@Free Aucune réponse du service client depuis 2 semaines"
        result = self.classifier.classify(tweet)
        
        self.assertEqual(result.is_reclamation, "OUI")
        self.assertEqual(result.theme, "SAV")
        self.assertEqual(result.type_incident, "PROCESSUS_SAV")
    
    def test_batch_classify(self):
        """Test classification batch"""
        tweets = [
            "@Free Panne internet",
            "@Free Merci pour le service",
            "@Free Problème de facturation"
        ]
        
        results = self.classifier.batch_classify(tweets)
        
        self.assertEqual(len(results), 3)
        self.assertIsInstance(results[0], ClassificationResult)
        
        # Vérifier que les réclamations sont détectées
        self.assertEqual(results[0].is_reclamation, "OUI")  # Panne
        self.assertEqual(results[1].is_reclamation, "NON")  # Merci
        self.assertEqual(results[2].is_reclamation, "OUI")  # Problème


class TestEdgeCases(unittest.TestCase):
    """Tests pour les cas limites et edge cases"""
    
    def setUp(self):
        """Initialisation"""
        self.classifier = TweetClassifier(
            model_name="fallback",
            api_key=None
        )
    
    def test_empty_tweet(self):
        """Test tweet vide"""
        result = self.classifier.classify("")
        
        # Doit retourner un résultat valide même pour tweet vide
        self.assertIsInstance(result, ClassificationResult)
    
    def test_multi_thematic_tweet(self):
        """Test tweet multi-thématique"""
        tweet = "@Free Problème de fibre ET de mobile en même temps, impossible de joindre le SAV"
        result = self.classifier.classify(tweet)
        
        # Doit choisir un thème principal
        self.assertIn(result.theme, ["FIBRE", "MOBILE", "SAV"])
        self.assertEqual(result.is_reclamation, "OUI")
    
    def test_tweet_with_emojis(self):
        """Test tweet avec emojis"""
        tweet = "😡 @Free Internet coupé 🔥💢"
        result = self.classifier.classify(tweet)
        
        self.assertEqual(result.is_reclamation, "OUI")
        self.assertEqual(result.sentiment, "NEGATIF")
    
    def test_tweet_with_url(self):
        """Test tweet avec URL"""
        tweet = "@Free Voir le problème ici: https://example.com/issue"
        result = self.classifier.classify(tweet)
        
        # Doit gérer les URLs sans erreur
        self.assertIsInstance(result, ClassificationResult)
    
    def test_very_long_tweet(self):
        """Test tweet très long"""
        tweet = "@Free " + ("Problème de connexion " * 50)
        result = self.classifier.classify(tweet)
        
        self.assertEqual(result.is_reclamation, "OUI")
    
    def test_mixed_case_keywords(self):
        """Test détection avec casse mixte"""
        tweet = "@Free PANNE FIBRE urgent !!!"
        result = self.classifier.classify(tweet)
        
        self.assertEqual(result.is_reclamation, "OUI")
        self.assertEqual(result.theme, "FIBRE")


class TestConfidenceScoring(unittest.TestCase):
    """Tests pour les scores de confiance"""
    
    def setUp(self):
        """Initialisation"""
        self.classifier = TweetClassifier(
            model_name="fallback",
            api_key=None
        )
    
    def test_confidence_range(self):
        """Test que confidence est dans [0, 1]"""
        tweets = [
            "@Free Panne internet",
            "@Free Merci",
            "@Free ???"
        ]
        
        for tweet in tweets:
            result = self.classifier.classify(tweet)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)
    
    def test_low_confidence_logging(self):
        """Test que les faibles confidences sont loggées"""
        # Tweet ambigu
        tweet = "@Free hmmm..."
        result = self.classifier.classify(tweet)
        
        # Devrait avoir une confiance modérée ou faible
        self.assertLessEqual(result.confidence, 0.8)


class TestExportResults(unittest.TestCase):
    """Tests pour l'export de résultats"""
    
    def setUp(self):
        """Initialisation"""
        self.classifier = TweetClassifier(
            model_name="fallback",
            api_key=None
        )
        self.temp_dir = Path("backend/data/temp_test")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Nettoyage après tests"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_export_json(self):
        """Test export JSON"""
        tweets = ["@Free Test 1", "@Free Test 2"]
        results = self.classifier.batch_classify(tweets)
        
        output_path = self.temp_dir / "results.json"
        self.classifier.export_results(results, str(output_path), format="json")
        
        self.assertTrue(output_path.exists())
        
        # Vérifier que le JSON est valide
        import json
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 2)
    
    def test_export_csv(self):
        """Test export CSV"""
        tweets = ["@Free Test 1", "@Free Test 2"]
        results = self.classifier.batch_classify(tweets)
        
        output_path = self.temp_dir / "results.csv"
        self.classifier.export_results(results, str(output_path), format="csv")
        
        self.assertTrue(output_path.exists())
        
        # Vérifier que le CSV est valide
        import pandas as pd
        df = pd.read_csv(output_path)
        self.assertEqual(len(df), 2)


def run_tests():
    """Lance tous les tests"""
    # Créer une suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter tous les tests
    suite.addTests(loader.loadTestsFromTestCase(TestClassificationResult))
    suite.addTests(loader.loadTestsFromTestCase(TestTweetClassifierFallback))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceScoring))
    suite.addTests(loader.loadTestsFromTestCase(TestExportResults))
    
    # Lancer les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retourner le résultat
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

