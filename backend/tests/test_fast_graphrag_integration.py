"""
Tests d'intégration pour Fast-GraphRAG avec ChatbotService
Vérifie le mécanisme de fallback et la gestion des erreurs
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chatbot_service import ChatbotService
from app.services.fast_graphrag_service import FastGraphRAGService
from app.models import KnowledgeDocument

class TestFastGraphRAGIntegration:
    """Tests d'intégration Fast-GraphRAG + ChatbotService"""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock du gestionnaire de base de données"""
        db_manager = Mock()
        db_manager.search_documents_by_embedding = AsyncMock(return_value=[
            {
                'id': 'doc1',
                'title': 'Test Document 1',
                'content': 'Contenu du document de test 1',
                'document_type': 'faq',
                'source_url': 'https://test.com/doc1',
                'source_domain': 'test.com',
                'content_hash': 'a' * 64,
                'usage_count': 5,
                'relevance_score': 0.85,
                'similarity_score': 0.75
            }
        ])
        db_manager.store_conversation_with_id = AsyncMock(return_value='conv_test_123')
        db_manager.store_message = AsyncMock(return_value='msg_test_123')
        db_manager.database_type = 'postgresql'
        return db_manager
    
    @pytest.fixture
    def chatbot_service(self, mock_db_manager):
        """Instance du ChatbotService avec mocks"""
        with patch.dict(os.environ, {'ENABLE_FAST_GRAPHRAG': 'false'}):
            service = ChatbotService(db_manager=mock_db_manager)
        return service
    
    @pytest.mark.asyncio
    async def test_graphrag_disabled_uses_vector_search(self, chatbot_service, mock_db_manager):
        """Test: Quand GraphRAG est désactivé, utilise la recherche vectorielle"""
        # Arrange
        query = "Comment configurer mon APN Free Mobile?"
        
        # Mock de l'embedding
        with patch.object(chatbot_service.doc_scraper, '_generate_embeddings', return_value=[0.1] * 384):
            # Act
            results = await chatbot_service._search_relevant_documents(query, max_results=5)
        
        # Assert
        assert len(results) > 0
        assert mock_db_manager.search_documents_by_embedding.called
        doc, score = results[0]
        assert isinstance(doc, KnowledgeDocument)
        assert doc.title == 'Test Document 1'
        assert score == 0.75
    
    @pytest.mark.asyncio
    async def test_graphrag_enabled_success(self, mock_db_manager):
        """Test: Quand GraphRAG est activé et fonctionne, utilise GraphRAG"""
        # Arrange
        with patch.dict(os.environ, {'ENABLE_FAST_GRAPHRAG': 'true'}):
            with patch('app.services.chatbot_service.FastGraphRAGService') as MockGraphRAG:
                # Mock du service GraphRAG
                mock_graphrag_instance = Mock()
                mock_graphrag_instance.query_graph = AsyncMock(return_value=[
                    {
                        'content': 'Résultat GraphRAG pertinent',
                        'score': 0.85,
                        'node_id': 'node_123'
                    }
                ])
                mock_graphrag_instance.is_initialized = True
                MockGraphRAG.return_value = mock_graphrag_instance
                
                service = ChatbotService(db_manager=mock_db_manager)
                query = "Comment configurer mon APN?"
                
                # Act
                results = await service._search_relevant_documents(query, max_results=5)
        
        # Assert
        assert len(results) > 0
        doc, score = results[0]
        assert isinstance(doc, KnowledgeDocument)
        assert doc.content == 'Résultat GraphRAG pertinent'
        assert score == 0.85
        assert doc.source_domain == 'fast-graphrag'
    
    @pytest.mark.asyncio
    async def test_graphrag_timeout_fallback(self, mock_db_manager):
        """Test: Timeout GraphRAG déclenche le fallback vers recherche vectorielle"""
        # Arrange
        with patch.dict(os.environ, {'ENABLE_FAST_GRAPHRAG': 'true', 'GRAPHRAG_TIMEOUT': '0.1'}):
            with patch('app.services.chatbot_service.FastGraphRAGService') as MockGraphRAG:
                # Mock du service GraphRAG avec timeout
                mock_graphrag_instance = Mock()
                
                async def slow_query(*args, **kwargs):
                    await asyncio.sleep(1.0)  # Plus long que le timeout
                    return []
                
                mock_graphrag_instance.query_graph = slow_query
                mock_graphrag_instance.is_initialized = True
                MockGraphRAG.return_value = mock_graphrag_instance
                
                service = ChatbotService(db_manager=mock_db_manager)
                query = "Test timeout"
                
                # Mock de l'embedding pour le fallback
                with patch.object(service.doc_scraper, '_generate_embeddings', return_value=[0.1] * 384):
                    # Act
                    results = await service._search_relevant_documents(query, max_results=5)
        
        # Assert
        assert len(results) > 0  # Fallback a fonctionné
        assert mock_db_manager.search_documents_by_embedding.called
        doc, score = results[0]
        assert doc.source_domain == 'test.com'  # Résultat du fallback
    
    @pytest.mark.asyncio
    async def test_graphrag_error_fallback(self, mock_db_manager):
        """Test: Erreur GraphRAG déclenche le fallback vers recherche vectorielle"""
        # Arrange
        with patch.dict(os.environ, {'ENABLE_FAST_GRAPHRAG': 'true'}):
            with patch('app.services.chatbot_service.FastGraphRAGService') as MockGraphRAG:
                # Mock du service GraphRAG avec erreur
                mock_graphrag_instance = Mock()
                mock_graphrag_instance.query_graph = AsyncMock(side_effect=Exception("GraphRAG error"))
                mock_graphrag_instance.is_initialized = True
                MockGraphRAG.return_value = mock_graphrag_instance
                
                service = ChatbotService(db_manager=mock_db_manager)
                query = "Test error"
                
                # Mock de l'embedding pour le fallback
                with patch.object(service.doc_scraper, '_generate_embeddings', return_value=[0.1] * 384):
                    # Act
                    results = await service._search_relevant_documents(query, max_results=5)
        
        # Assert
        assert len(results) > 0  # Fallback a fonctionné
        assert mock_db_manager.search_documents_by_embedding.called
    
    @pytest.mark.asyncio
    async def test_graphrag_low_score_fallback(self, mock_db_manager):
        """Test: Scores GraphRAG trop bas déclenchent le fallback"""
        # Arrange
        with patch.dict(os.environ, {'ENABLE_FAST_GRAPHRAG': 'true', 'GRAPHRAG_MIN_SCORE': '0.7'}):
            with patch('app.services.chatbot_service.FastGraphRAGService') as MockGraphRAG:
                # Mock du service GraphRAG avec scores faibles
                mock_graphrag_instance = Mock()
                mock_graphrag_instance.query_graph = AsyncMock(return_value=[
                    {
                        'content': 'Résultat peu pertinent',
                        'score': 0.3,  # En dessous du seuil
                        'node_id': 'node_456'
                    }
                ])
                mock_graphrag_instance.is_initialized = True
                MockGraphRAG.return_value = mock_graphrag_instance
                
                service = ChatbotService(db_manager=mock_db_manager)
                query = "Test low score"
                
                # Mock de l'embedding pour le fallback
                with patch.object(service.doc_scraper, '_generate_embeddings', return_value=[0.1] * 384):
                    # Act
                    results = await service._search_relevant_documents(query, max_results=5)
        
        # Assert
        assert len(results) > 0  # Fallback a fonctionné
        assert mock_db_manager.search_documents_by_embedding.called
    
    @pytest.mark.asyncio
    async def test_process_message_with_graphrag(self, mock_db_manager):
        """Test: process_message utilise GraphRAG correctement"""
        # Arrange
        with patch.dict(os.environ, {'ENABLE_FAST_GRAPHRAG': 'true'}):
            with patch('app.services.chatbot_service.FastGraphRAGService') as MockGraphRAG:
                # Mock du service GraphRAG
                mock_graphrag_instance = Mock()
                mock_graphrag_instance.query_graph = AsyncMock(return_value=[
                    {
                        'content': 'Documentation APN Free Mobile',
                        'score': 0.9,
                        'node_id': 'apn_doc'
                    }
                ])
                mock_graphrag_instance.is_initialized = True
                MockGraphRAG.return_value = mock_graphrag_instance
                
                service = ChatbotService(db_manager=mock_db_manager)
                
                # Mock de la génération LLM
                with patch.object(service, '_generate_llm_response', return_value="Voici comment configurer votre APN"):
                    # Act
                    result = await service.process_message(
                        message="Comment configurer mon APN?",
                        conversation_id="conv_test_123",
                        llm_provider="ollama"
                    )
        
        # Assert
        assert result['success'] is True
        assert 'response' in result
        assert result['documents_found'] > 0
        assert 'processing_time' in result
    
    @pytest.mark.asyncio
    async def test_graphrag_initialization_failure(self, mock_db_manager):
        """Test: Échec d'initialisation GraphRAG n'empêche pas le service de fonctionner"""
        # Arrange
        with patch.dict(os.environ, {'ENABLE_FAST_GRAPHRAG': 'true'}):
            with patch('app.services.chatbot_service.FastGraphRAGService', side_effect=Exception("Init failed")):
                # Act
                service = ChatbotService(db_manager=mock_db_manager)
        
        # Assert
        assert service.graphrag_enabled is False
        assert service.fast_graphrag is None
        
        # Vérifier que le service fonctionne quand même
        query = "Test sans GraphRAG"
        with patch.object(service.doc_scraper, '_generate_embeddings', return_value=[0.1] * 384):
            results = await service._search_relevant_documents(query, max_results=5)
        
        assert len(results) > 0  # Fallback fonctionne

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

