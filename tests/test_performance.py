"""
Tests de Performance - Latence et Scalabilité
==============================================

Mesure des performances pour validation avant production.
"""

import unittest
import time
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


class TestCleaningPerformance(unittest.TestCase):
    """Tests de performance du nettoyage"""
    
    def test_cleaning_small_dataset(self):
        """Test: Nettoyage de 500 tweets < 1s"""
        # Génération de données
        tweets = [f"@Free tweet numéro {i} http://test.com 😊" for i in range(500)]
        df = pd.DataFrame({'text': tweets})
        
        cleaner = TweetCleaner()
        
        # Mesure du temps
        start = time.time()
        df_cleaned, stats = cleaner.process_dataframe(df, 'text')
        elapsed = time.time() - start
        
        # Validation
        self.assertLess(elapsed, 1.0, f"Nettoyage trop lent: {elapsed:.2f}s (attendu < 1s)")
        self.assertEqual(len(df_cleaned), len(df))  # Pas de doublons dans cet exemple
        
        print(f"✅ Performance nettoyage 500 tweets: {elapsed:.3f}s")
    
    def test_cleaning_large_dataset(self):
        """Test: Nettoyage de 5000 tweets < 5s (conforme specs)"""
        # Génération de données
        tweets = [f"Tweet #{i} avec @mention et http://url.com" for i in range(5000)]
        df = pd.DataFrame({'text': tweets})
        
        cleaner = TweetCleaner()
        
        # Mesure du temps
        start = time.time()
        df_cleaned, stats = cleaner.process_dataframe(df, 'text')
        elapsed = time.time() - start
        
        # Validation conforme specs: < 5s pour 5000 tweets
        self.assertLess(elapsed, 5.0, f"Nettoyage trop lent: {elapsed:.2f}s (attendu < 5s)")
        
        print(f"✅ Performance nettoyage 5000 tweets: {elapsed:.3f}s")
    
    def test_deduplication_performance(self):
        """Test: Performance de la déduplication MD5"""
        # Dataset avec 50% de doublons
        unique_tweets = [f"Tweet unique {i}" for i in range(1000)]
        all_tweets = unique_tweets + unique_tweets  # 2000 tweets (1000 doublons)
        df = pd.DataFrame({'text': all_tweets})
        
        # Mesure
        start = time.time()
        df_dedup = TweetCleaner.remove_duplicates(df, 'text')
        elapsed = time.time() - start
        
        # Validation
        self.assertEqual(len(df_dedup), 1000)  # 50% retirés
        self.assertLess(elapsed, 1.0, f"Déduplication trop lente: {elapsed:.2f}s")
        
        print(f"✅ Déduplication 2000→1000 tweets: {elapsed:.3f}s")


class TestClassificationPerformance(unittest.TestCase):
    """Tests de performance de la classification"""
    
    def setUp(self):
        self.classifier = MistralClassifier(batch_size=50)
    
    def test_fallback_classification_speed(self):
        """Test: Performance du classificateur fallback"""
        tweets = [f"Tweet test numéro {i}" for i in range(100)]
        
        start = time.time()
        results = self.classifier._classify_batch_fallback(tweets)
        elapsed = time.time() - start
        
        # Le fallback doit être très rapide
        self.assertLess(elapsed, 0.5, f"Fallback trop lent: {elapsed:.2f}s")
        self.assertEqual(len(results), 100)
        
        print(f"✅ Fallback 100 tweets: {elapsed:.3f}s")
    
    @patch('streamlit.progress')
    @patch('streamlit.empty')
    def test_batch_processing_scalability(self, mock_empty, mock_progress):
        """Test: Scalabilité du batch processing"""
        # Mock pour éviter appel réel à Ollama
        df_100 = pd.DataFrame({'text_cleaned': [f"Tweet {i}" for i in range(100)]})
        df_500 = pd.DataFrame({'text_cleaned': [f"Tweet {i}" for i in range(500)]})
        
        with patch.object(self.classifier, 'classify_batch') as mock_classify:
            # Retour mocké
            mock_classify.return_value = [
                {'index': 0, 'sentiment': 'neutre', 'categorie': 'autre', 'score_confiance': 0.5}
            ]
            
            # Test 100 tweets
            start = time.time()
            self.classifier.classify_dataframe(df_100, 'text_cleaned', show_progress=False)
            time_100 = time.time() - start
            
            # Test 500 tweets
            start = time.time()
            self.classifier.classify_dataframe(df_500, 'text_cleaned', show_progress=False)
            time_500 = time.time() - start
            
            # Scalabilité: temps doit être linéaire (avec tolérance)
            ratio = time_500 / time_100
            self.assertLess(ratio, 10, f"Scalabilité non linéaire: ratio={ratio}")
            
            print(f"✅ Scalabilité: 100 tweets={time_100:.3f}s, 500 tweets={time_500:.3f}s, ratio={ratio:.2f}x")
    
    def test_memory_usage(self):
        """Test: Utilisation mémoire < 1GB (conforme specs)"""
        import psutil
        import os as os_module
        
        process = psutil.Process(os_module.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Traitement d'un dataset important
        df = pd.DataFrame({'text_cleaned': [f"Tweet #{i}" for i in range(5000)]})
        
        with patch.object(self.classifier, 'classify_batch') as mock:
            mock.return_value = [{'index': 0, 'sentiment': 'neutre', 'categorie': 'autre', 'score_confiance': 0.5}]
            self.classifier.classify_dataframe(df, 'text_cleaned', show_progress=False)
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before
        
        # Conforme specs: < 1GB (1024 MB)
        self.assertLess(mem_used, 1024, f"Mémoire excessive: {mem_used:.1f}MB")
        
        print(f"✅ Mémoire utilisée: {mem_used:.1f}MB (< 1GB)")


class TestLatencyMeasurement(unittest.TestCase):
    """Tests de latence pour SLA"""
    
    def test_response_time_single_tweet(self):
        """Test: Latence pour un tweet unique"""
        classifier = MistralClassifier()
        
        start = time.time()
        result = classifier._classify_batch_fallback(["Test tweet"])
        latency = time.time() - start
        
        # Un tweet doit être traité en < 100ms (fallback)
        self.assertLess(latency, 0.1, f"Latence excessive: {latency*1000:.1f}ms")
        
        print(f"✅ Latence 1 tweet: {latency*1000:.1f}ms")
    
    def test_throughput_batch(self):
        """Test: Débit en tweets/seconde"""
        classifier = MistralClassifier(batch_size=50)
        tweets = [f"Tweet {i}" for i in range(50)]
        
        start = time.time()
        results = classifier._classify_batch_fallback(tweets)
        elapsed = time.time() - start
        
        throughput = len(tweets) / elapsed if elapsed > 0 else 0
        
        # Fallback doit être très rapide (> 100 tweets/s)
        self.assertGreater(throughput, 100, f"Débit insuffisant: {throughput:.1f} tweets/s")
        
        print(f"✅ Débit fallback: {throughput:.1f} tweets/s")


if __name__ == '__main__':
    unittest.main(verbosity=2)

