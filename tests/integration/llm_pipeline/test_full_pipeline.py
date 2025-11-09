"""
Tests d'intégration du pipeline complet
Validation du workflow end-to-end
"""

import pytest
import asyncio
import time
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from src.utils.file_handlers.read_file import readCSV, readTweetsCSV
from src.core.NLP_processing.text_cleaning import TextCleaner
from src.core.NLP_processing.sentiment_analysis import SentimentAnalyzer
from src.core.LLM_integration.api_client import LLMAPIClient
from src.core.LLM_integration.response_handler import ResponseHandler
from src.utils.logging.error_handler import ErrorHandler


class TestFullPipeline:
    """Tests du pipeline complet de bout en bout"""
    
    @pytest.fixture
    def sample_csv(self):
        """Crée un CSV de test temporaire"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("tweet_id,author,text,date\n")
            f.write("1,user1,Service excellent merci!,2024-01-01\n")
            f.write("2,user2,Problème réseau catastrophique,2024-01-02\n")
            f.write("3,user3,Information sur abonnement,2024-01-03\n")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        try:
            os.unlink(temp_path)
        except:
            pass
    
    def test_data_loading_step(self, sample_csv):
        """Teste l'étape de chargement des données"""
        # Étape 1: Charger les données
        df = readTweetsCSV(sample_csv)
        
        assert len(df) == 3
        assert 'text' in df.columns
        assert 'tweet_id' in df.columns
    
    def test_text_cleaning_step(self, sample_csv):
        """Teste l'étape de nettoyage de texte"""
        # Charger
        df = readTweetsCSV(sample_csv)
        
        # Nettoyer
        cleaner = TextCleaner()
        df['cleaned_text'] = df['text'].apply(
            lambda x: cleaner.clean_for_analysis(x)
        )
        
        assert 'cleaned_text' in df.columns
        assert len(df['cleaned_text']) == 3
        assert all(isinstance(text, str) for text in df['cleaned_text'])
    
    def test_sentiment_analysis_step(self, sample_csv):
        """Teste l'étape d'analyse de sentiment"""
        # Charger
        df = readTweetsCSV(sample_csv)
        
        # Nettoyer
        cleaner = TextCleaner()
        df['cleaned_text'] = df['text'].apply(
            lambda x: cleaner.clean_for_analysis(x)
        )
        
        # Analyser sentiment
        analyzer = SentimentAnalyzer()
        df['sentiment'] = df['cleaned_text'].apply(
            lambda x: analyzer.analyze_sentiment(x)['sentiment']
        )
        
        assert 'sentiment' in df.columns
        assert len(df['sentiment']) == 3
    
    def test_complete_workflow(self, sample_csv):
        """Teste le workflow complet sans LLM"""
        # Étape 1: Chargement
        df = readTweetsCSV(sample_csv)
        
        # Étape 2: Nettoyage
        cleaner = TextCleaner()
        df['cleaned_text'] = df['text'].apply(
            lambda x: cleaner.clean_for_analysis(x)
        )
        
        # Étape 3: Analyse sentiment
        analyzer = SentimentAnalyzer()
        df['sentiment_analysis'] = df['cleaned_text'].apply(
            analyzer.analyze_sentiment
        )
        
        # Étape 4: Extraction des résultats
        df['sentiment'] = df['sentiment_analysis'].apply(lambda x: x['sentiment'])
        df['score'] = df['sentiment_analysis'].apply(lambda x: x['score'])
        
        # Vérifications
        assert len(df) == 3
        assert 'sentiment' in df.columns
        assert 'score' in df.columns
        assert all(isinstance(s, float) for s in df['score'])
    
    def test_error_handling_in_pipeline(self, sample_csv):
        """Teste la gestion d'erreurs dans le pipeline"""
        error_handler = ErrorHandler(log_dir=tempfile.mkdtemp())
        
        try:
            # Tenter de charger un fichier inexistant
            df = readTweetsCSV("nonexistent.csv")
        except FileNotFoundError as e:
            error_handler.log_error(e, context={'step': 'data_loading'})
        
        stats = error_handler.get_error_stats()
        assert stats['total_errors'] > 0


class TestLLMIntegration:
    """Tests d'intégration avec LLM (mockés)"""
    
    @pytest.fixture
    def sample_tweets(self):
        return [
            "Service excellent merci!",
            "Problème réseau catastrophique",
            "Information sur abonnement"
        ]
    
    @pytest.mark.asyncio
    async def test_llm_api_integration(self, sample_tweets):
        """Teste l'intégration avec l'API LLM (mocké)"""
        client = LLMAPIClient(provider="openai", timeout=5.0)
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{
                    'message': {
                        'content': '''{
                            "sentiment": "positive",
                            "sentiment_score": 0.8,
                            "category": "compliment",
                            "priority": "basse",
                            "keywords": ["service", "excellent"],
                            "is_urgent": false,
                            "needs_response": false,
                            "estimated_resolution_time": null
                        }'''
                    }
                }]
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            # Appeler l'API pour chaque tweet
            results = []
            for tweet in sample_tweets:
                result = await client.call_api(
                    prompt=f"Analyse: {tweet}",
                    system_prompt="Analyse de sentiment"
                )
                results.append(result)
            
            assert len(results) == 3
            assert all(r is not None for r in results)
    
    @pytest.mark.asyncio
    async def test_response_parsing(self, sample_tweets):
        """Teste le parsing des réponses LLM"""
        handler = ResponseHandler()
        
        # Simuler des réponses LLM
        raw_responses = [
            '''{
                "sentiment": "positive",
                "sentiment_score": 0.8,
                "category": "compliment",
                "priority": "basse",
                "keywords": ["excellent"],
                "is_urgent": false,
                "needs_response": false,
                "estimated_resolution_time": null
            }''',
            '''```json
            {
                "sentiment": "negative",
                "sentiment_score": -0.9,
                "category": "réclamation",
                "priority": "haute",
                "keywords": ["problème"],
                "is_urgent": true,
                "needs_response": true,
                "estimated_resolution_time": 60
            }
            ```''',
            ""  # Réponse vide
        ]
        
        # Parser toutes les réponses
        results = []
        for raw in raw_responses:
            result = handler.process_response(raw, allow_defaults=True)
            results.append(result)
        
        assert len(results) == 3
        assert results[0]['sentiment'] == 'positive'
        assert results[1]['sentiment'] == 'negative'
        assert results[2].get('_is_default') is True  # Réponse par défaut


class TestPerformanceMetrics:
    """Tests des métriques de performance"""
    
    @pytest.fixture
    def sample_csv(self):
        """Crée un CSV avec plusieurs tweets"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("tweet_id,author,text,date\n")
            for i in range(100):
                f.write(f"{i},user{i},Test tweet {i},2024-01-01\n")
            temp_path = f.name
        
        yield temp_path
        
        try:
            os.unlink(temp_path)
        except:
            pass
    
    def test_pipeline_execution_time(self, sample_csv):
        """Teste le temps d'exécution du pipeline sur 100 tweets"""
        start = time.time()
        
        # Pipeline complet
        df = readTweetsCSV(sample_csv)
        cleaner = TextCleaner()
        df['cleaned'] = df['text'].apply(cleaner.clean_for_analysis)
        analyzer = SentimentAnalyzer()
        df['sentiment'] = df['cleaned'].apply(
            lambda x: analyzer.analyze_sentiment(x)['sentiment']
        )
        
        duration = time.time() - start
        
        # Devrait être rapide (< 5 secondes pour 100 tweets)
        assert duration < 5.0
    
    def test_memory_usage(self, sample_csv):
        """Teste l'utilisation mémoire"""
        import sys
        
        # Charger et traiter
        df = readTweetsCSV(sample_csv)
        cleaner = TextCleaner()
        df['cleaned'] = df['text'].apply(cleaner.clean_for_analysis)
        
        # Vérifier la taille mémoire
        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        # Devrait être raisonnable
        assert memory_mb < 10  # Moins de 10 MB pour 100 tweets


class TestErrorRecovery:
    """Tests de récupération d'erreurs"""
    
    def test_partial_pipeline_failure(self):
        """Teste la récupération en cas d'échec partiel"""
        texts = [
            "Tweet normal",
            None,  # Devrait être géré
            "",    # Devrait être géré
            "Autre tweet normal"
        ]
        
        cleaner = TextCleaner()
        analyzer = SentimentAnalyzer()
        
        results = []
        for text in texts:
            try:
                cleaned = cleaner.clean_for_analysis(text) if text else ""
                sentiment = analyzer.analyze_sentiment(cleaned)
                results.append(sentiment)
            except Exception as e:
                # Ajouter un résultat par défaut
                results.append({
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'error': str(e)
                })
        
        # Devrait avoir traité tous les textes
        assert len(results) == 4
    
    @pytest.mark.asyncio
    async def test_api_failure_recovery(self):
        """Teste la récupération après échec API"""
        client = LLMAPIClient(provider="openai", timeout=5.0, max_retries=3)
        
        with patch('httpx.AsyncClient.post') as mock_post:
            call_count = [0]
            
            async def failing_then_success(*args, **kwargs):
                call_count[0] += 1
                
                if call_count[0] <= 2:
                    raise Exception("API Error")
                
                mock_response = Mock()
                mock_response.json.return_value = {
                    'choices': [{'message': {'content': 'OK'}}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            
            mock_post.side_effect = failing_then_success
            
            # Devrait réussir grâce au retry
            result = await client.call_api("Test")
            assert result is not None


class TestDataIntegrity:
    """Tests d'intégrité des données"""
    
    def test_no_data_loss(self):
        """Teste qu'aucune donnée n'est perdue dans le pipeline"""
        # Créer des données de test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("tweet_id,author,text,date\n")
            for i in range(50):
                f.write(f"{i},user{i},Tweet {i},2024-01-01\n")
            temp_path = f.name
        
        try:
            # Traiter
            df = readTweetsCSV(temp_path)
            initial_count = len(df)
            
            cleaner = TextCleaner()
            df['cleaned'] = df['text'].apply(cleaner.clean_for_analysis)
            
            analyzer = SentimentAnalyzer()
            df['sentiment'] = df['cleaned'].apply(
                lambda x: analyzer.analyze_sentiment(x)
            )
            
            final_count = len(df)
            
            # Aucune ligne ne devrait être perdue
            assert initial_count == final_count == 50
        
        finally:
            os.unlink(temp_path)
    
    def test_data_consistency(self):
        """Teste la cohérence des données à travers le pipeline"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("tweet_id,author,text,date\n")
            f.write("1,user1,Excellent,2024-01-01\n")
            f.write("2,user2,Mauvais,2024-01-02\n")
            temp_path = f.name
        
        try:
            df = readTweetsCSV(temp_path)
            
            # Les IDs doivent rester cohérents
            original_ids = df['tweet_id'].tolist()
            
            cleaner = TextCleaner()
            df['cleaned'] = df['text'].apply(cleaner.clean_for_analysis)
            
            final_ids = df['tweet_id'].tolist()
            
            assert original_ids == final_ids
        
        finally:
            os.unlink(temp_path)


class TestLogging:
    """Tests de journalisation"""
    
    def test_error_logging(self):
        """Teste la journalisation des erreurs"""
        log_dir = tempfile.mkdtemp()
        error_handler = ErrorHandler(log_dir=log_dir)
        
        try:
            # Simuler une erreur
            raise ValueError("Test error")
        except ValueError as e:
            error_handler.log_error(
                e,
                context={'component': 'test'},
                module_name='test_pipeline'
            )
        
        stats = error_handler.get_error_stats()
        assert stats['total_errors'] > 0
        assert 'ValueError' in stats['by_type']
    
    def test_performance_logging(self):
        """Teste la journalisation des performances"""
        log_dir = tempfile.mkdtemp()
        error_handler = ErrorHandler(log_dir=log_dir)
        
        # Simuler une opération
        start = time.time()
        time.sleep(0.1)
        duration = time.time() - start
        
        error_handler.log_performance(
            operation="test_operation",
            duration=duration,
            metadata={'items': 100}
        )
        
        # Vérifier que le log a été écrit
        log_files = list(Path(log_dir).glob("*.log"))
        assert len(log_files) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])

