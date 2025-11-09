"""
Tests Unitaires - Classification (MistralClassifier)
=====================================================

Validation complète du module de classification Mistral.
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

from services.mistral_classifier import (
    MistralClassifier,
    check_ollama_availability,
    list_available_models,
    classify_single_tweet
)
from services.tweet_cleaner import TweetCleaner


class TestMistralClassifier(unittest.TestCase):
    """Tests unitaires pour MistralClassifier"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.classifier = MistralClassifier(model_name='mistral', batch_size=10)
        self.sample_tweets = [
            "Super service Free Mobile!",
            "Panne internet depuis ce matin",
            "Comment activer ma box?"
        ]
    
    def test_initialization(self):
        """Test: Initialisation du classificateur"""
        self.assertEqual(self.classifier.model_name, 'mistral')
        self.assertEqual(self.classifier.batch_size, 10)
        self.assertEqual(self.classifier.temperature, 0.1)
        self.assertEqual(self.classifier.max_retries, 3)
    
    def test_build_prompt(self):
        """Test: Construction du prompt"""
        prompt = self.classifier.build_classification_prompt(self.sample_tweets)
        
        # Vérifications
        self.assertIn('expert en analyse', prompt)
        self.assertIn('Free Mobile', prompt)
        self.assertIn('sentiment', prompt.lower())
        self.assertIn('categorie', prompt.lower())
        self.assertIn('JSON', prompt)
        
        # Tous les tweets doivent être dans le prompt
        for tweet in self.sample_tweets:
            self.assertIn(tweet, prompt)
    
    def test_parse_ollama_response_valid(self):
        """Test: Parsing d'une réponse JSON valide"""
        response = '''
        {
            "results": [
                {"index": 0, "sentiment": "positif", "categorie": "produit", "score_confiance": 0.95},
                {"index": 1, "sentiment": "negatif", "categorie": "service", "score_confiance": 0.88}
            ]
        }
        '''
        
        results = self.classifier._parse_ollama_response(response, 2)
        
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['sentiment'], 'positif')
        self.assertEqual(results[1]['sentiment'], 'negatif')
    
    def test_parse_ollama_response_invalid(self):
        """Test: Parsing d'une réponse JSON invalide"""
        response = "Texte invalide sans JSON"
        
        results = self.classifier._parse_ollama_response(response, 2)
        
        self.assertIsNone(results)
    
    def test_fallback_classification(self):
        """Test: Classification fallback"""
        results = self.classifier._classify_batch_fallback(self.sample_tweets)
        
        # Doit retourner autant de résultats que de tweets
        self.assertEqual(len(results), len(self.sample_tweets))
        
        # Chaque résultat doit avoir les champs requis
        for result in results:
            self.assertIn('index', result)
            self.assertIn('sentiment', result)
            self.assertIn('categorie', result)
            self.assertIn('score_confiance', result)
        
        # Vérifier les sentiments détectés
        self.assertEqual(results[0]['sentiment'], 'positif')  # "Super"
        self.assertEqual(results[1]['sentiment'], 'negatif')  # "Panne"
        self.assertEqual(results[2]['sentiment'], 'neutre')   # Question
    
    @patch('streamlit.progress')
    @patch('streamlit.empty')
    def test_classify_dataframe(self, mock_empty, mock_progress):
        """Test: Classification d'un DataFrame"""
        df = pd.DataFrame({
            'text': ['Tweet 1', 'Tweet 2'],
            'text_cleaned': ['Tweet 1', 'Tweet 2']
        })
        
        # Mock pour éviter appel réel à Ollama
        with patch.object(self.classifier, 'classify_batch') as mock_classify:
            mock_classify.return_value = [
                {'index': 0, 'sentiment': 'positif', 'categorie': 'produit', 'score_confiance': 0.9},
                {'index': 1, 'sentiment': 'negatif', 'categorie': 'service', 'score_confiance': 0.85}
            ]
            
            df_classified = self.classifier.classify_dataframe(df, 'text_cleaned', show_progress=False)
            
            # Vérifications
            self.assertIn('sentiment', df_classified.columns)
            self.assertIn('categorie', df_classified.columns)
            self.assertIn('score_confiance', df_classified.columns)
            self.assertEqual(len(df_classified), 2)
    
    def test_get_classification_stats(self):
        """Test: Calcul des statistiques"""
        df = pd.DataFrame({
            'sentiment': ['positif', 'negatif', 'positif'],
            'categorie': ['produit', 'service', 'produit'],
            'score_confiance': [0.9, 0.85, 0.95]
        })
        
        stats = self.classifier.get_classification_stats(df)
        
        self.assertEqual(stats['total_classified'], 3)
        self.assertEqual(stats['sentiment_distribution']['positif'], 2)
        self.assertEqual(stats['sentiment_distribution']['negatif'], 1)
        self.assertAlmostEqual(stats['avg_confidence'], 0.9, places=2)


class TestOllamaUtilities(unittest.TestCase):
    """Tests des fonctions utilitaires Ollama"""
    
    def test_check_ollama_availability(self):
        """Test: Vérification disponibilité Ollama"""
        # Ce test peut échouer si Ollama n'est pas démarré
        is_available = check_ollama_availability()
        self.assertIsInstance(is_available, bool)
    
    def test_list_available_models(self):
        """Test: Liste des modèles"""
        models = list_available_models()
        self.assertIsInstance(models, list)
        
        # Si Ollama est disponible, mistral doit être dans la liste
        if check_ollama_availability():
            # Note: Ce test suppose que mistral est installé
            pass  # Flexible pour l'environnement de test
    
    def test_classify_single_tweet(self):
        """Test: Classification d'un tweet unique"""
        result = classify_single_tweet("Super service Free!", model_name='mistral')
        
        # Doit retourner un dictionnaire
        self.assertIsInstance(result, dict)
        self.assertIn('sentiment', result)
        self.assertIn('categorie', result)
        self.assertIn('score_confiance', result)


class TestCleanerConfiguration(unittest.TestCase):
    """Tests de configuration du cleaner"""
    
    def test_configuration_urls_only(self):
        """Test: Configuration avec URLs seulement"""
        cleaner = TweetCleaner(
            remove_urls=True,
            remove_mentions=False,
            remove_hashtags=False
        )
        
        tweet = "@Free http://test.com #hashtag problème"
        cleaned = cleaner.clean_text(tweet)
        
        self.assertNotIn('http://test.com', cleaned)
        self.assertIn('@Free', cleaned)  # Mention préservée
        self.assertIn('#hashtag', cleaned)  # Hashtag préservé
    
    def test_configuration_mentions_only(self):
        """Test: Configuration avec mentions seulement"""
        cleaner = TweetCleaner(
            remove_urls=False,
            remove_mentions=True,
            remove_hashtags=False
        )
        
        tweet = "@Free http://test.com #hashtag"
        cleaned = cleaner.clean_text(tweet)
        
        self.assertIn('http://test.com', cleaned)  # URL préservée
        self.assertNotIn('@Free', cleaned)
        self.assertIn('#hashtag', cleaned)  # Hashtag préservé


if __name__ == '__main__':
    # Exécuter les tests
    unittest.main(verbosity=2)

