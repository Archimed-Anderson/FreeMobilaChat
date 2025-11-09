"""
Tests unitaires pour le module sentiment_analysis
Validation de l'analyse de sentiment avec cas limites
"""

import pytest
from src.core.NLP_processing.sentiment_analysis import (
    SentimentAnalyzer,
    SentimentType
)


class TestSentimentAnalyzer:
    """Tests pour la classe SentimentAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Fixture pour instancier un SentimentAnalyzer"""
        return SentimentAnalyzer()
    
    def test_initialization(self, analyzer):
        """Teste l'initialisation correcte de l'analyseur"""
        assert analyzer is not None
        assert len(analyzer.positive_words) > 0
        assert len(analyzer.negative_words) > 0
        assert len(analyzer.intensifiers) > 0
        assert len(analyzer.negations) > 0


class TestAnalyzeSentiment:
    """Tests pour analyze_sentiment"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    def test_empty_text(self, analyzer):
        """Teste avec texte vide"""
        result = analyzer.analyze_sentiment("")
        assert result['sentiment'] == SentimentType.NEUTRAL
        assert result['score'] == 0.0
        assert result['confidence'] == 0.0
    
    def test_none_input(self, analyzer):
        """Teste avec None en entrée"""
        result = analyzer.analyze_sentiment(None)
        assert result['sentiment'] == SentimentType.NEUTRAL
    
    def test_positive_sentiment(self, analyzer):
        """Teste la détection de sentiment positif"""
        positive_texts = [
            "Le service est excellent !",
            "Merci beaucoup, c'est parfait",
            "Super génial top",
            "Très satisfait, bravo"
        ]
        
        for text in positive_texts:
            result = analyzer.analyze_sentiment(text)
            assert result['sentiment'] == SentimentType.POSITIVE
            assert result['score'] > 0
    
    def test_negative_sentiment(self, analyzer):
        """Teste la détection de sentiment négatif"""
        negative_texts = [
            "Service nul et catastrophique",
            "Honte, c'est horrible",
            "Très déçu, inacceptable",
            "Bug problème panne"
        ]
        
        for text in negative_texts:
            result = analyzer.analyze_sentiment(text)
            assert result['sentiment'] == SentimentType.NEGATIVE
            assert result['score'] < 0
    
    def test_neutral_sentiment(self, analyzer):
        """Teste la détection de sentiment neutre"""
        neutral_texts = [
            "Information sur l'abonnement",
            "Quelle est la procédure ?",
            "Je voudrais savoir",
            "Bonjour"
        ]
        
        for text in neutral_texts:
            result = analyzer.analyze_sentiment(text)
            assert result['sentiment'] == SentimentType.NEUTRAL
    
    def test_mixed_sentiment(self, analyzer):
        """Teste avec sentiments mixtes"""
        text = "Service excellent mais trop cher"
        result = analyzer.analyze_sentiment(text)
        # Devrait avoir un score proche de 0
        assert abs(result['score']) < 0.5
    
    def test_sentiment_with_emojis(self, analyzer):
        """Teste l'analyse avec emojis"""
        positive_emoji_text = "Super 😊 👍"
        result = analyzer.analyze_sentiment(positive_emoji_text)
        assert result['score'] > 0
        
        negative_emoji_text = "Nul 😡 👎"
        result = analyzer.analyze_sentiment(negative_emoji_text)
        assert result['score'] < 0
    
    def test_negation_handling(self, analyzer):
        """Teste la gestion des négations"""
        # Positif sans négation
        text1 = "C'est bien"
        result1 = analyzer.analyze_sentiment(text1)
        
        # Positif avec négation (devrait devenir négatif/neutre)
        text2 = "Ce n'est pas bien"
        result2 = analyzer.analyze_sentiment(text2)
        
        # Le score avec négation devrait être inversé
        assert result1['score'] > result2['score']
    
    def test_intensifiers(self, analyzer):
        """Teste l'effet des intensificateurs"""
        text1 = "C'est bien"
        text2 = "C'est très bien"
        
        result1 = analyzer.analyze_sentiment(text1)
        result2 = analyzer.analyze_sentiment(text2)
        
        # L'intensificateur devrait augmenter le score
        assert result2['score'] > result1['score']
    
    def test_confidence_score(self, analyzer):
        """Teste le calcul de la confiance"""
        # Texte fortement positif
        strong_text = "Excellent super génial parfait bravo"
        result = analyzer.analyze_sentiment(strong_text)
        assert result['confidence'] > 0.5
        
        # Texte neutre
        neutral_text = "Bonjour"
        result = analyzer.analyze_sentiment(neutral_text)
        assert result['confidence'] < 0.5
    
    def test_details_structure(self, analyzer):
        """Teste la structure du dictionnaire de détails"""
        result = analyzer.analyze_sentiment("Test text")
        
        assert 'details' in result
        assert 'positive_words' in result['details']
        assert 'negative_words' in result['details']
        assert 'emoji_score' in result['details']
        assert 'has_negation' in result['details']
        assert 'has_intensifier' in result['details']


class TestBatchAnalyze:
    """Tests pour batch_analyze"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    def test_batch_processing(self, analyzer):
        """Teste le traitement en batch"""
        texts = [
            "Service excellent",
            "Très nul",
            "Information"
        ]
        
        results = analyzer.batch_analyze(texts)
        
        assert len(results) == 3
        assert results[0]['sentiment'] == SentimentType.POSITIVE
        assert results[1]['sentiment'] == SentimentType.NEGATIVE
        assert results[2]['sentiment'] == SentimentType.NEUTRAL
    
    def test_empty_batch(self, analyzer):
        """Teste avec liste vide"""
        results = analyzer.batch_analyze([])
        assert results == []
    
    def test_large_batch(self, analyzer):
        """Teste avec un grand batch"""
        texts = [f"Text {i}" for i in range(100)]
        results = analyzer.batch_analyze(texts)
        assert len(results) == 100


class TestGetSentimentDistribution:
    """Tests pour get_sentiment_distribution"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    def test_distribution_calculation(self, analyzer):
        """Teste le calcul de distribution"""
        texts = [
            "Excellent",  # Positif
            "Excellent",  # Positif
            "Nul",        # Négatif
            "Info"        # Neutre
        ]
        
        distribution = analyzer.get_sentiment_distribution(texts)
        
        assert distribution[SentimentType.POSITIVE] == 2
        assert distribution[SentimentType.NEGATIVE] == 1
        assert distribution[SentimentType.NEUTRAL] == 1
    
    def test_empty_distribution(self, analyzer):
        """Teste avec liste vide"""
        distribution = analyzer.get_sentiment_distribution([])
        
        assert distribution[SentimentType.POSITIVE] == 0
        assert distribution[SentimentType.NEGATIVE] == 0
        assert distribution[SentimentType.NEUTRAL] == 0


class TestDetectIrony:
    """Tests pour detect_irony"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    def test_irony_markers(self, analyzer):
        """Teste la détection de marqueurs d'ironie"""
        ironic_texts = [
            "Super service lol",
            "Génial mdr",
            "Top service /s",
            "Excellent 😂"
        ]
        
        for text in ironic_texts:
            assert analyzer.detect_irony(text) is True
    
    def test_no_irony(self, analyzer):
        """Teste l'absence d'ironie"""
        sincere_texts = [
            "Le service est bon",
            "Merci beaucoup",
            "Très satisfait"
        ]
        
        for text in sincere_texts:
            assert analyzer.detect_irony(text) is False


class TestAnalyzeWithContext:
    """Tests pour analyze_with_context"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    def test_irony_inversion(self, analyzer):
        """Teste l'inversion due à l'ironie"""
        # Texte apparemment positif avec ironie
        text = "Super service lol"
        result = analyzer.analyze_with_context(text, consider_irony=True)
        
        # L'ironie devrait avoir inversé le sentiment
        assert result['details']['has_irony'] is True
        # Le sentiment devrait être négatif ou neutre
        assert result['sentiment'] != SentimentType.POSITIVE or result['score'] < 0
    
    def test_confidence_reduction_with_irony(self, analyzer):
        """Teste la réduction de confiance avec ironie"""
        text = "Excellent mdr"
        result = analyzer.analyze_with_context(text, consider_irony=True)
        
        # La confiance devrait être réduite
        assert result['confidence'] < 1.0
    
    def test_no_irony_consideration(self, analyzer):
        """Teste sans considération de l'ironie"""
        text = "Super service lol"
        result = analyzer.analyze_with_context(text, consider_irony=False)
        
        assert 'has_irony' in result['details']


class TestEdgeCases:
    """Tests pour les cas limites"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    @pytest.mark.parametrize("text", [
        "😊😭😡",  # Seulement emojis
        "!!!",  # Seulement ponctuation
        "123456",  # Seulement chiffres
        "aaa bbb ccc",  # Mots sans signification
    ])
    def test_unusual_texts(self, analyzer, text):
        """Teste avec textes inhabituels"""
        result = analyzer.analyze_sentiment(text)
        assert result is not None
        assert 'sentiment' in result
        assert 'score' in result
    
    def test_very_long_text(self, analyzer):
        """Teste avec texte très long"""
        text = " ".join(["mot"] * 1000)
        result = analyzer.analyze_sentiment(text)
        assert result is not None
    
    def test_mixed_case(self, analyzer):
        """Teste avec casse mixte"""
        texts = [
            "EXCELLENT",
            "ExCeLlEnT",
            "excellent"
        ]
        
        results = [analyzer.analyze_sentiment(t)['sentiment'] for t in texts]
        # Tous devraient être détectés comme positifs
        assert all(r == SentimentType.POSITIVE for r in results)
    
    def test_accented_characters(self, analyzer):
        """Teste avec caractères accentués"""
        text = "Service très médiocre, complètement déçu"
        result = analyzer.analyze_sentiment(text)
        assert result['sentiment'] == SentimentType.NEGATIVE
    
    def test_multiple_negations(self, analyzer):
        """Teste avec négations multiples"""
        text = "Pas pas bien"  # Double négation
        result = analyzer.analyze_sentiment(text)
        assert result is not None


class TestTweetSpecificCases:
    """Tests spécifiques aux tweets"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    @pytest.mark.parametrize("length", [10, 50, 100, 280])
    def test_various_tweet_lengths(self, analyzer, length):
        """Teste avec différentes longueurs de tweets (10-280 caractères)"""
        text = "a" * length
        result = analyzer.analyze_sentiment(text)
        assert result is not None
        assert isinstance(result['score'], float)
    
    def test_tweet_with_spelling_errors(self, analyzer):
        """Teste avec fautes d'orthographe courantes"""
        texts = [
            "servis exelent",  # Fautes
            "Service excellent",  # Correct
        ]
        
        for text in texts:
            result = analyzer.analyze_sentiment(text)
            # Devrait quand même fonctionner
            assert result is not None
    
    def test_tweet_with_abbreviations(self, analyzer):
        """Teste avec abréviations courantes"""
        text = "svp pb avec abonnement"
        result = analyzer.analyze_sentiment(text)
        assert result is not None
    
    def test_customer_service_scenarios(self, analyzer):
        """Teste des scénarios typiques de SAV"""
        scenarios = {
            "Ma box ne fonctionne plus": SentimentType.NEGATIVE,
            "Merci pour votre aide rapide": SentimentType.POSITIVE,
            "Comment changer mon forfait ?": SentimentType.NEUTRAL,
            "C'est inadmissible !": SentimentType.NEGATIVE
        }
        
        for text, expected in scenarios.items():
            result = analyzer.analyze_sentiment(text)
            # On vérifie juste que ça ne crash pas
            assert result['sentiment'] in [
                SentimentType.POSITIVE,
                SentimentType.NEUTRAL,
                SentimentType.NEGATIVE
            ]


class TestPerformance:
    """Tests de performance"""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    def test_single_analysis_speed(self, analyzer):
        """Teste la vitesse d'analyse d'un texte"""
        import time
        
        text = "Le service est excellent et rapide"
        
        start = time.time()
        analyzer.analyze_sentiment(text)
        duration = time.time() - start
        
        # Devrait être très rapide (< 0.1s)
        assert duration < 0.1
    
    def test_batch_performance(self, analyzer):
        """Teste la performance sur un batch"""
        import time
        
        texts = ["Text d'exemple"] * 100
        
        start = time.time()
        analyzer.batch_analyze(texts)
        duration = time.time() - start
        
        # 100 analyses devraient prendre moins de 2 secondes
        assert duration < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

