"""
Tests d'Intégration - Workflow Complet
=======================================

Validation du workflow end-to-end.
"""

import unittest
import pandas as pd
import sys
import os
from unittest.mock import patch, MagicMock

# Ajout du chemin pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

# Mock streamlit pour les tests
sys.modules['streamlit'] = MagicMock()

from services.tweet_cleaner import TweetCleaner
from services.mistral_classifier import MistralClassifier
from services.tweet_visualizer import export_results_csv


class TestCompleteWorkflow(unittest.TestCase):
    """Tests du workflow complet Upload → Nettoyage → Classification → Export"""
    
    def setUp(self):
        """Setup pour chaque test"""
        self.sample_data = pd.DataFrame({
            'text': [
                "@Free super service http://test.com 😊",
                "Panne fibre depuis ce matin @Freebox",
                "Comment activer ma box? #help",
                "@Free super service http://test.com 😊",  # Doublon
                "Prix compétitifs, je recommande!"
            ]
        })
    
    def test_end_to_end_workflow(self):
        """Test: Workflow complet end-to-end"""
        # ÉTAPE 1: Nettoyage
        cleaner = TweetCleaner()
        df_cleaned, cleaning_stats = cleaner.process_dataframe(self.sample_data, 'text')
        
        # Validation nettoyage
        self.assertIn('text_cleaned', df_cleaned.columns)
        self.assertLess(len(df_cleaned), len(self.sample_data))  # Doublon retiré
        self.assertEqual(cleaning_stats['duplicates_removed'], 1)
        
        # ÉTAPE 2: Classification (avec fallback pour les tests)
        classifier = MistralClassifier(batch_size=10)
        
        with patch.object(classifier, 'classify_batch') as mock_classify:
            # Mock le retour d'Ollama
            mock_classify.return_value = [
                {'index': i, 'sentiment': 'neutre', 'categorie': 'autre', 'score_confiance': 0.7}
                for i in range(len(df_cleaned))
            ]
            
            df_classified = classifier.classify_dataframe(
                df_cleaned,
                'text_cleaned',
                show_progress=False
            )
        
        # Validation classification
        self.assertIn('sentiment', df_classified.columns)
        self.assertIn('categorie', df_classified.columns)
        self.assertIn('score_confiance', df_classified.columns)
        self.assertEqual(len(df_classified), len(df_cleaned))
        
        # ÉTAPE 3: Export
        csv_data = export_results_csv(df_classified)
        
        # Validation export
        self.assertIsInstance(csv_data, bytes)
        self.assertGreater(len(csv_data), 0)
        
        print(f"✅ Workflow complet: {len(self.sample_data)} → {len(df_cleaned)} → {len(df_classified)} tweets")
    
    def test_data_integrity_through_pipeline(self):
        """Test: Intégrité des données à travers le pipeline"""
        # Données avec ID unique
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'text': ['Tweet 1', 'Tweet 2', 'Tweet 3']
        })
        
        # Nettoyage
        cleaner = TweetCleaner()
        df_cleaned, _ = cleaner.process_dataframe(df, 'text')
        
        # Les IDs doivent être préservés
        self.assertIn('id', df_cleaned.columns)
        self.assertTrue(all(df_cleaned['id'].isin([1, 2, 3])))
        
        print("✅ Intégrité des données: IDs préservés")
    
    def test_error_recovery(self):
        """Test: Récupération en cas d'erreur"""
        # DataFrame avec données problématiques
        df = pd.DataFrame({
            'text': [None, '', 'Tweet valide', None]
        })
        
        cleaner = TweetCleaner()
        
        # Ne doit pas crasher
        try:
            df_cleaned, stats = cleaner.process_dataframe(df, 'text')
            # Au moins le tweet valide doit passer
            self.assertGreaterEqual(len(df_cleaned), 1)
            print("✅ Récupération d'erreur: traitement gracieux des données invalides")
        except Exception as e:
            self.fail(f"Le système a crashé sur des données invalides: {e}")


class TestConcurrency(unittest.TestCase):
    """Tests de traitement concurrent"""
    
    def test_multiple_classifications_sequential(self):
        """Test: Classifications multiples séquentielles"""
        classifier = MistralClassifier()
        
        # Plusieurs classifications successives
        tweets_batch1 = ["Tweet A", "Tweet B"]
        tweets_batch2 = ["Tweet C", "Tweet D"]
        
        results1 = classifier._classify_batch_fallback(tweets_batch1)
        results2 = classifier._classify_batch_fallback(tweets_batch2)
        
        # Les résultats doivent être indépendants
        self.assertEqual(len(results1), 2)
        self.assertEqual(len(results2), 2)
        self.assertEqual(results1[0]['index'], 0)
        self.assertEqual(results2[0]['index'], 0)
        
        print("✅ Classifications séquentielles: résultats indépendants")


class TestModelVersioning(unittest.TestCase):
    """Tests de versioning des modèles"""
    
    def test_classification_metadata(self):
        """Test: Métadonnées de classification présentes"""
        classifier = MistralClassifier(model_name='mistral')
        df = pd.DataFrame({'text_cleaned': ['Test']})
        
        with patch.object(classifier, 'classify_batch') as mock:
            mock.return_value = [
                {'index': 0, 'sentiment': 'neutre', 'categorie': 'autre', 'score_confiance': 0.5}
            ]
            
            df_classified = classifier.classify_dataframe(df, 'text_cleaned', show_progress=False)
        
        # Métadonnées doivent être présentes
        self.assertIn('classification_method', df_classified.columns)
        self.assertIn('model_name', df_classified.columns)
        self.assertIn('classification_timestamp', df_classified.columns)
        
        # Valeurs correctes
        self.assertEqual(df_classified['classification_method'].iloc[0], 'mistral')
        self.assertEqual(df_classified['model_name'].iloc[0], 'mistral')
        
        print("✅ Versioning: métadonnées de classification présentes")
    
    def test_reproducibility(self):
        """Test: Reproductibilité des classifications"""
        classifier = MistralClassifier(temperature=0.1)  # Faible température
        
        tweet = "Service excellent Free Mobile"
        
        # Deux classifications du même tweet
        result1 = classifier._classify_batch_fallback([tweet])
        result2 = classifier._classify_batch_fallback([tweet])
        
        # Avec fallback, les résultats doivent être identiques
        self.assertEqual(result1[0]['sentiment'], result2[0]['sentiment'])
        self.assertEqual(result1[0]['categorie'], result2[0]['categorie'])
        
        print("✅ Reproductibilité: classifications cohérentes")


class TestAPIValidation(unittest.TestCase):
    """Tests de validation de l'API"""
    
    def test_classifier_stats_format(self):
        """Test: Format des statistiques du classificateur"""
        classifier = MistralClassifier()
        
        df = pd.DataFrame({
            'sentiment': ['positif', 'negatif', 'neutre'],
            'categorie': ['produit', 'service', 'produit'],
            'score_confiance': [0.9, 0.85, 0.75]
        })
        
        stats = classifier.get_classification_stats(df)
        
        # Vérifier la structure
        required_keys = ['total_classified', 'sentiment_distribution', 
                        'categorie_distribution', 'avg_confidence', 
                        'min_confidence', 'max_confidence']
        
        for key in required_keys:
            self.assertIn(key, stats, f"Clé manquante: {key}")
        
        # Vérifier les valeurs
        self.assertEqual(stats['total_classified'], 3)
        self.assertAlmostEqual(stats['avg_confidence'], 0.833, places=2)
        
        print("✅ API Stats: format correct et valeurs cohérentes")


if __name__ == '__main__':
    import time
    unittest.main(verbosity=2)

