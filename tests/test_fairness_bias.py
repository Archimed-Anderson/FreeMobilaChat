"""
Tests d'Équité et de Biais - Détection de Discrimination
==========================================================

Validation de l'équité des prédictions du modèle.
Détecte les biais potentiels dans les classifications.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from collections import Counter
from unittest.mock import MagicMock

# Ajout du chemin pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'streamlit_app'))

# Mock streamlit pour les tests
sys.modules['streamlit'] = MagicMock()

from services.mistral_classifier import MistralClassifier


class TestSentimentFairness(unittest.TestCase):
    """Tests d'équité dans l'analyse de sentiment"""
    
    def setUp(self):
        self.classifier = MistralClassifier()
    
    def test_no_gender_bias(self):
        """Test: Pas de biais de genre dans le sentiment"""
        # Tweets identiques avec pronoms différents
        tweets_male = [
            "Il est satisfait du service",
            "Il a un problème avec sa box",
            "Il demande de l'aide"
        ]
        
        tweets_female = [
            "Elle est satisfaite du service",
            "Elle a un problème avec sa box",
            "Elle demande de l'aide"
        ]
        
        # Classification
        results_male = self.classifier._classify_batch_fallback(tweets_male)
        results_female = self.classifier._classify_batch_fallback(tweets_female)
        
        # Les sentiments doivent être identiques
        sentiments_male = [r['sentiment'] for r in results_male]
        sentiments_female = [r['sentiment'] for r in results_female]
        
        self.assertEqual(sentiments_male, sentiments_female, 
                        "Biais de genre détecté dans le sentiment")
        
        print(f"✅ Pas de biais de genre: {sentiments_male} == {sentiments_female}")
    
    def test_no_regional_bias(self):
        """Test: Pas de biais géographique"""
        # Tweets similaires avec villes différentes
        tweets = [
            "Panne à Paris",
            "Panne à Marseille",
            "Panne à Lyon",
            "Panne à Toulouse"
        ]
        
        results = self.classifier._classify_batch_fallback(tweets)
        sentiments = [r['sentiment'] for r in results]
        
        # Tous les sentiments doivent être identiques (négatif car "panne")
        unique_sentiments = set(sentiments)
        self.assertEqual(len(unique_sentiments), 1, 
                        f"Biais régional détecté: {sentiments}")
        self.assertEqual(sentiments[0], 'negatif')
        
        print(f"✅ Pas de biais régional: tous classés '{sentiments[0]}'")
    
    def test_category_distribution_balance(self):
        """Test: Distribution équilibrée des catégories"""
        # Dataset équilibré
        tweets = [
            "Problème de débit fibre",  # produit
            "Service client excellent",  # service
            "Aide pour installation",    # support
            "Nouvelle offre promotionnelle"  # promotion
        ]
        
        results = self.classifier._classify_batch_fallback(tweets)
        categories = [r['categorie'] for r in results]
        
        # Distribution doit être variée
        unique_categories = set(categories)
        self.assertGreaterEqual(len(unique_categories), 2, 
                               "Classification trop homogène, biais possible")
        
        print(f"✅ Distribution catégories: {Counter(categories)}")
    
    def test_confidence_consistency(self):
        """Test: Cohérence des scores de confiance"""
        # Tweets très clairs vs ambigus
        clear_tweets = [
            "Service excellent, merci beaucoup!",  # Clairement positif
            "Panne totale, catastrophe, nul"       # Clairement négatif
        ]
        
        ambiguous_tweets = [
            "Bon service mais cher",               # Ambigu
            "Installation ok mais bugs parfois"    # Ambigu
        ]
        
        results_clear = self.classifier._classify_batch_fallback(clear_tweets)
        results_ambiguous = self.classifier._classify_batch_fallback(ambiguous_tweets)
        
        # Confiance des tweets clairs doit être > ambigus
        avg_conf_clear = np.mean([r['score_confiance'] for r in results_clear])
        avg_conf_ambiguous = np.mean([r['score_confiance'] for r in results_ambiguous])
        
        self.assertGreater(avg_conf_clear, avg_conf_ambiguous,
                          "Les tweets clairs devraient avoir une confiance plus élevée")
        
        print(f"✅ Confiance claire={avg_conf_clear:.2f} > ambigüe={avg_conf_ambiguous:.2f}")


class TestBiasDetection(unittest.TestCase):
    """Tests de détection de biais"""
    
    def setUp(self):
        self.classifier = MistralClassifier()
    
    def test_no_price_bias(self):
        """Test: Pas de biais selon le prix mentionné"""
        tweets = [
            "Forfait à 10€ excellent",
            "Forfait à 50€ excellent"
        ]
        
        results = self.classifier._classify_batch_fallback(tweets)
        sentiments = [r['sentiment'] for r in results]
        
        # Le prix ne doit pas influencer le sentiment
        self.assertEqual(sentiments[0], sentiments[1],
                        "Biais de prix détecté")
        
        print(f"✅ Pas de biais de prix: {sentiments}")
    
    def test_no_time_bias(self):
        """Test: Pas de biais temporel"""
        tweets = [
            "Panne ce matin",
            "Panne ce soir",
            "Panne hier",
            "Panne demain"
        ]
        
        results = self.classifier._classify_batch_fallback(tweets)
        sentiments = [r['sentiment'] for r in results]
        
        # Tous doivent être négatifs (panne)
        unique = set(sentiments)
        self.assertEqual(len(unique), 1)
        self.assertEqual(sentiments[0], 'negatif')
        
        print(f"✅ Pas de biais temporel: tous '{sentiments[0]}'")
    
    def test_balanced_positive_negative(self):
        """Test: Équilibre dans la détection positif/négatif"""
        positive_tweets = [f"Super service {i}" for i in range(50)]
        negative_tweets = [f"Panne problème {i}" for i in range(50)]
        
        results_pos = self.classifier._classify_batch_fallback(positive_tweets)
        results_neg = self.classifier._classify_batch_fallback(negative_tweets)
        
        # Comptage
        positive_count = sum(1 for r in results_pos if r['sentiment'] == 'positif')
        negative_count = sum(1 for r in results_neg if r['sentiment'] == 'negatif')
        
        # Au moins 80% correctement classés
        self.assertGreater(positive_count / 50, 0.8, "Sous-détection du positif")
        self.assertGreater(negative_count / 50, 0.8, "Sous-détection du négatif")
        
        print(f"✅ Équilibre: {positive_count}/50 positifs, {negative_count}/50 négatifs détectés")


class TestCategorizationFairness(unittest.TestCase):
    """Tests d'équité dans la catégorisation"""
    
    def setUp(self):
        self.classifier = MistralClassifier()
    
    def test_product_category_consistency(self):
        """Test: Cohérence de la catégorie 'produit'"""
        product_tweets = [
            "Problème fibre optique",
            "Souci avec mobile 5G",
            "Box qui lag"
        ]
        
        results = self.classifier._classify_batch_fallback(product_tweets)
        categories = [r['categorie'] for r in results]
        
        # Tous doivent être catégorisés comme 'produit'
        product_count = sum(1 for cat in categories if cat == 'produit')
        self.assertGreater(product_count / len(product_tweets), 0.6,
                          "Catégorisation 'produit' incohérente")
        
        print(f"✅ Catégorie produit: {product_count}/{len(product_tweets)} correctement détectés")
    
    def test_no_category_dominance(self):
        """Test: Pas de sur-représentation d'une catégorie"""
        diverse_tweets = [
            "Excellent débit fibre",        # produit
            "Service client réactif",       # service
            "Besoin d'aide installation",   # support
            "Nouvelle promo intéressante",  # promotion
            "Information générale"          # autre
        ]
        
        results = self.classifier._classify_batch_fallback(diverse_tweets)
        categories = [r['categorie'] for r in results]
        category_counts = Counter(categories)
        
        # Aucune catégorie ne doit dominer excessivement
        max_count = max(category_counts.values())
        self.assertLessEqual(max_count / len(diverse_tweets), 0.5,
                            "Une catégorie domine trop")
        
        print(f"✅ Distribution équilibrée: {dict(category_counts)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)

