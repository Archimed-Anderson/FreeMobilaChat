"""
Tests Unitaires - Prétraitement (TweetCleaner)
===============================================

Validation complète du module de nettoyage de tweets.
"""

import unittest
import pandas as pd
import sys
import os

# Ajout du chemin pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

from services.tweet_cleaner import TweetCleaner, clean_tweet_text, batch_clean_tweets


class TestTweetCleaner(unittest.TestCase):
    """Tests unitaires pour TweetCleaner"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.cleaner = TweetCleaner()
        self.sample_tweets = [
            "@Free panne internet http://test.com 😊",
            "Super service #FreeMobile merci!",
            "@Freebox bug depuis 2h www.example.com",
            "@Free panne internet http://test.com 😊"  # Doublon
        ]
    
    def test_remove_duplicates(self):
        """Test: Suppression des doublons par MD5"""
        df = pd.DataFrame({'text': self.sample_tweets})
        df_dedup = TweetCleaner.remove_duplicates(df, 'text')
        
        # Doit retirer 1 doublon (4 → 3 tweets)
        self.assertEqual(len(df_dedup), 3)
        self.assertEqual(len(df), 4)
    
    def test_clean_text_urls(self):
        """Test: Suppression des URLs"""
        tweet = "Problème @Free http://test.com et www.example.com"
        cleaned = self.cleaner.clean_text(tweet)
        
        # URLs doivent être supprimées
        self.assertNotIn('http://test.com', cleaned)
        self.assertNotIn('www.example.com', cleaned)
        self.assertIn('Problème', cleaned)
    
    def test_clean_text_mentions(self):
        """Test: Suppression des mentions @"""
        tweet = "@Free @Freebox problème internet"
        cleaned = self.cleaner.clean_text(tweet)
        
        # Mentions doivent être supprimées
        self.assertNotIn('@Free', cleaned)
        self.assertNotIn('@Freebox', cleaned)
        self.assertIn('problème', cleaned)
    
    def test_clean_text_hashtags(self):
        """Test: Suppression des hashtags (optionnel)"""
        cleaner_with_hashtags = TweetCleaner(remove_hashtags=True)
        tweet = "Super #FreeMobile #Fibre service"
        cleaned = cleaner_with_hashtags.clean_text(tweet)
        
        # Hashtags doivent être supprimés si activé
        self.assertNotIn('#FreeMobile', cleaned)
        self.assertNotIn('#Fibre', cleaned)
    
    def test_clean_text_emojis(self):
        """Test: Conversion des emojis"""
        tweet = "Service excellent 😊👍"
        cleaned = self.cleaner.clean_text(tweet)
        
        # Emojis doivent être convertis en texte
        self.assertIn('Service excellent', cleaned)
        # Emojis ne doivent plus être présents sous forme unicode
    
    def test_process_dataframe(self):
        """Test: Pipeline complet de nettoyage"""
        df = pd.DataFrame({'text': self.sample_tweets})
        df_cleaned, stats = self.cleaner.process_dataframe(df, 'text')
        
        # Vérifications des stats
        self.assertEqual(stats['total_original'], 4)
        self.assertEqual(stats['duplicates_removed'], 1)
        self.assertEqual(stats['total_cleaned'], 3)
        
        # Nouvelle colonne créée
        self.assertIn('text_cleaned', df_cleaned.columns)
        
        # Longueur moyenne doit être calculée
        self.assertGreater(stats['avg_length_before'], 0)
        self.assertGreater(stats['avg_length_after'], 0)
    
    def test_empty_text_handling(self):
        """Test: Gestion des valeurs manquantes"""
        df = pd.DataFrame({'text': ['Tweet valide', None, '', 'Autre tweet']})
        df_cleaned, stats = self.cleaner.process_dataframe(df, 'text')
        
        # Valeurs manquantes doivent être supprimées
        self.assertLess(len(df_cleaned), len(df))
        self.assertEqual(stats['empty_tweets'], 1)  # None compte comme vide
    
    def test_helper_function(self):
        """Test: Fonction helper clean_tweet_text"""
        tweet = "@Free http://test.com panne"
        cleaned = clean_tweet_text(tweet)
        
        self.assertNotIn('@Free', cleaned)
        self.assertNotIn('http://test.com', cleaned)
        self.assertIn('panne', cleaned)
    
    def test_batch_clean(self):
        """Test: Nettoyage par lot"""
        tweets = ["@Free test", "http://example.com info"]
        cleaned = batch_clean_tweets(tweets)
        
        self.assertEqual(len(cleaned), 2)
        self.assertNotIn('@Free', cleaned[0])
        self.assertNotIn('http://example.com', cleaned[1])


class TestTweetCleanerEdgeCases(unittest.TestCase):
    """Tests des cas limites"""
    
    def setUp(self):
        self.cleaner = TweetCleaner()
    
    def test_empty_dataframe(self):
        """Test: DataFrame vide"""
        df = pd.DataFrame({'text': []})
        df_cleaned, stats = self.cleaner.process_dataframe(df, 'text')
        
        self.assertEqual(len(df_cleaned), 0)
        self.assertEqual(stats['total_original'], 0)
    
    def test_missing_column(self):
        """Test: Colonne manquante"""
        df = pd.DataFrame({'other': ['tweet']})
        df_cleaned, stats = self.cleaner.process_dataframe(df, 'text')
        
        # Ne doit pas crasher
        self.assertEqual(len(df_cleaned), len(df))
    
    def test_special_characters(self):
        """Test: Caractères spéciaux"""
        tweet = "Test avec émojis 🎉🎊 et caractères spéciaux éàç"
        cleaned = self.cleaner.clean_text(tweet)
        
        # Ne doit pas crasher
        self.assertIsInstance(cleaned, str)
        self.assertGreater(len(cleaned), 0)
    
    def test_very_long_tweet(self):
        """Test: Tweet très long"""
        tweet = "Test " * 1000  # 5000 caractères
        cleaned = self.cleaner.clean_text(tweet)
        
        self.assertIsInstance(cleaned, str)
        self.assertGreater(len(cleaned), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)

