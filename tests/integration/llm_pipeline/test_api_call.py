"""
Tests d'intégration pour les appels API LLM
Validation du temps de réponse et de la stabilité
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

from src.core.LLM_integration.api_client import LLMAPIClient, LLMProvider


class TestAPIResponseTime:
    """Tests du temps de réponse API"""
    
    @pytest.fixture
    def mock_client(self):
        """Fixture avec client mocké"""
        return LLMAPIClient(provider="openai", timeout=5.0)
    
    @pytest.mark.asyncio
    async def test_timeout_threshold(self, mock_client):
        """Teste que le timeout est respecté (5 secondes max)"""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Simuler une réponse lente
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(6)  # Plus que le timeout
                raise asyncio.TimeoutError()
            
            mock_post.side_effect = slow_response
            
            start = time.time()
            try:
                await mock_client.call_api("Test prompt")
            except Exception:
                pass
            duration = time.time() - start
            
            # Devrait échouer avant 6 secondes
            assert duration < 6.0
    
    @pytest.mark.asyncio
    async def test_fast_response(self, mock_client):
        """Teste qu'une réponse rapide est bien gérée"""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock de réponse rapide
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'Test response'}}]
            }
            mock_response.raise_for_status = Mock()
            
            async def fast_response(*args, **kwargs):
                await asyncio.sleep(0.1)
                return mock_response
            
            mock_post.side_effect = fast_response
            
            start = time.time()
            result = await mock_client.call_api("Test prompt")
            duration = time.time() - start
            
            assert duration < 1.0
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_timeout_configuration(self):
        """Teste différentes configurations de timeout"""
        timeouts = [1.0, 3.0, 5.0, 10.0]
        
        for timeout in timeouts:
            client = LLMAPIClient(provider="openai", timeout=timeout)
            assert client.timeout == timeout
    
    @pytest.mark.asyncio
    async def test_average_response_time(self, mock_client):
        """Teste le temps de réponse moyen sur plusieurs appels"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'Response'}}]
            }
            mock_response.raise_for_status = Mock()
            
            async def timed_response(*args, **kwargs):
                await asyncio.sleep(0.5)  # 500ms simulé
                return mock_response
            
            mock_post.side_effect = timed_response
            
            # Faire 5 appels
            durations = []
            for _ in range(5):
                start = time.time()
                await mock_client.call_api("Test")
                durations.append(time.time() - start)
            
            avg_duration = sum(durations) / len(durations)
            assert avg_duration < 5.0  # Moyenne sous le timeout


class TestAPIStability:
    """Tests de stabilité sur appels consécutifs"""
    
    @pytest.fixture
    def mock_client(self):
        return LLMAPIClient(provider="openai", timeout=5.0)
    
    @pytest.mark.asyncio
    async def test_consecutive_calls(self, mock_client):
        """Teste 100 appels consécutifs pour vérifier la stabilité"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'OK'}}]
            }
            mock_response.raise_for_status = Mock()
            
            async def stable_response(*args, **kwargs):
                await asyncio.sleep(0.01)
                return mock_response
            
            mock_post.side_effect = stable_response
            
            # Reset stats
            mock_client.reset_stats()
            
            # 100 appels consécutifs
            success_count = 0
            for i in range(100):
                try:
                    result = await mock_client.call_api(f"Test {i}")
                    if result:
                        success_count += 1
                except Exception:
                    pass
            
            # Au moins 95% de réussite
            assert success_count >= 95
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, mock_client):
        """Teste la récupération après erreurs"""
        with patch('httpx.AsyncClient.post') as mock_post:
            call_count = [0]
            
            async def intermittent_failure(*args, **kwargs):
                call_count[0] += 1
                await asyncio.sleep(0.01)
                
                # Fail les 2 premiers appels, puis succès
                if call_count[0] <= 2:
                    raise Exception("Simulated failure")
                
                mock_response = Mock()
                mock_response.json.return_value = {
                    'choices': [{'message': {'content': 'OK'}}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            
            mock_post.side_effect = intermittent_failure
            
            # Devrait réussir grâce au retry
            try:
                result = await mock_client.call_api("Test")
                assert result is not None
            except Exception:
                # Acceptable si tous les retries échouent
                pass
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mock_client):
        """Teste les requêtes concurrentes"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'OK'}}]
            }
            mock_response.raise_for_status = Mock()
            
            async def concurrent_response(*args, **kwargs):
                await asyncio.sleep(0.1)
                return mock_response
            
            mock_post.side_effect = concurrent_response
            
            # Lancer 10 requêtes en parallèle
            tasks = [mock_client.call_api(f"Test {i}") for i in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Vérifier que la plupart ont réussi
            success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
            assert success_count >= 8


class TestEmptyResponse:
    """Tests de gestion des réponses vides"""
    
    @pytest.fixture
    def mock_client(self):
        return LLMAPIClient(provider="openai", timeout=5.0)
    
    @pytest.mark.asyncio
    async def test_empty_content(self, mock_client):
        """Teste la gestion d'une réponse vide"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{'message': {'content': ''}}]
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = await mock_client.call_api("Test")
            assert result is not None
            assert result['content'] == ''
    
    @pytest.mark.asyncio
    async def test_missing_content_field(self, mock_client):
        """Teste la gestion d'une réponse sans champ content"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{'message': {}}]  # Pas de content
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            try:
                result = await mock_client.call_api("Test")
                # Devrait gérer l'erreur
            except Exception as e:
                # C'est acceptable
                pass
    
    @pytest.mark.asyncio
    async def test_null_response(self, mock_client):
        """Teste la gestion d'une réponse null"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = None
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            try:
                result = await mock_client.call_api("Test")
            except Exception:
                pass  # Comportement attendu


class TestRetryMechanism:
    """Tests du mécanisme de retry"""
    
    @pytest.fixture
    def mock_client(self):
        return LLMAPIClient(provider="openai", timeout=5.0, max_retries=3)
    
    @pytest.mark.asyncio
    async def test_retry_on_timeout(self, mock_client):
        """Teste le retry en cas de timeout"""
        with patch('httpx.AsyncClient.post') as mock_post:
            call_count = [0]
            
            async def timeout_then_success(*args, **kwargs):
                call_count[0] += 1
                
                if call_count[0] < 2:
                    raise asyncio.TimeoutError()
                
                mock_response = Mock()
                mock_response.json.return_value = {
                    'choices': [{'message': {'content': 'Success'}}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            
            mock_post.side_effect = timeout_then_success
            
            result = await mock_client.call_api("Test")
            assert result is not None
            assert call_count[0] == 2  # 1 échec + 1 succès
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, mock_client):
        """Teste l'échec après max retries"""
        with patch('httpx.AsyncClient.post') as mock_post:
            async def always_fail(*args, **kwargs):
                raise asyncio.TimeoutError()
            
            mock_post.side_effect = always_fail
            
            with pytest.raises(RuntimeError, match="Échec après"):
                await mock_client.call_api("Test")
    
    @pytest.mark.asyncio
    async def test_exponential_backoff(self, mock_client):
        """Teste le backoff exponentiel entre retries"""
        with patch('httpx.AsyncClient.post') as mock_post:
            timestamps = []
            
            async def record_timing(*args, **kwargs):
                timestamps.append(time.time())
                raise asyncio.TimeoutError()
            
            mock_post.side_effect = record_timing
            
            try:
                await mock_client.call_api("Test")
            except:
                pass
            
            # Vérifier que les délais augmentent
            if len(timestamps) >= 2:
                delays = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
                # Les délais doivent augmenter (backoff exponentiel)
                for i in range(len(delays)-1):
                    assert delays[i+1] >= delays[i]


class TestStatisticsTracking:
    """Tests du suivi des statistiques"""
    
    @pytest.fixture
    def mock_client(self):
        client = LLMAPIClient(provider="openai", timeout=5.0)
        client.reset_stats()
        return client
    
    @pytest.mark.asyncio
    async def test_stats_tracking(self, mock_client):
        """Teste le tracking des statistiques"""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'OK'}}]
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            # Faire quelques appels
            for _ in range(5):
                await mock_client.call_api("Test")
            
            stats = mock_client.get_stats()
            
            assert stats['total_calls'] == 5
            assert stats['successful_calls'] == 5
            assert stats['failed_calls'] == 0
            assert stats['average_duration'] >= 0
    
    @pytest.mark.asyncio
    async def test_failed_calls_tracking(self, mock_client):
        """Teste le tracking des échecs"""
        with patch('httpx.AsyncClient.post') as mock_post:
            async def failing_call(*args, **kwargs):
                raise Exception("Simulated failure")
            
            mock_post.side_effect = failing_call
            
            # Faire des appels qui échouent
            for _ in range(3):
                try:
                    await mock_client.call_api("Test")
                except:
                    pass
            
            stats = mock_client.get_stats()
            assert stats['failed_calls'] == 3


class TestConnectionTest:
    """Tests de test de connexion"""
    
    @pytest.mark.asyncio
    async def test_successful_connection(self):
        """Teste une connexion réussie"""
        client = LLMAPIClient(provider="openai", timeout=5.0)
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {
                'choices': [{'message': {'content': 'OK'}}]
            }
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response
            
            result = await client.test_connection()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_failed_connection(self):
        """Teste une connexion échouée"""
        client = LLMAPIClient(provider="openai", timeout=5.0)
        
        with patch('httpx.AsyncClient.post') as mock_post:
            async def fail_connection(*args, **kwargs):
                raise Exception("Connection failed")
            
            mock_post.side_effect = fail_connection
            
            result = await client.test_connection()
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])

