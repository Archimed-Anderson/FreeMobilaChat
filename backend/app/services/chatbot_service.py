"""
Chatbot SAV Service for FreeMobilaChat
Implements RAG (Retrieval-Augmented Generation) for intelligent customer service
"""

import asyncio
import json
import logging
import uuid
import os
from datetime import datetime, UTC
from typing import List, Dict, Optional, Any, Tuple
import hashlib

# Embeddings and similarity search
try:
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    SIMILARITY_AVAILABLE = True
except ImportError:
    SIMILARITY_AVAILABLE = False
    print("Similarity search dependencies not available. Install: pip install numpy scikit-learn")

# Agno Agent Framework
try:
    from agno.agent import Agent
    from agno.models.mistral import MistralChat
    from agno.models.ollama import Ollama
    AGNO_AVAILABLE = True
except ImportError as e:
    AGNO_AVAILABLE = False
    print(f"Agno dependencies not available: {e}. Install: pip install agno ollama")

from ..models import (
    ChatMessage, Conversation, KnowledgeDocument, ChatFeedback,
    MessageRole, ConversationStatus, FeedbackType
)
from ..services.llm_analyzer import LLMAnalyzer, LLMProvider
from ..services.documentation_scraper import DocumentationScraper
from ..services.fast_graphrag_service import FastGraphRAGService
from ..utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service principal du chatbot SAV intelligent"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialiser le service chatbot

        Args:
            db_manager: Gestionnaire de base de données
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # Vérifier les dépendances (mode dégradé si non disponibles)
        if not SIMILARITY_AVAILABLE:
            self.logger.warning("⚠️ Similarity search dependencies not available. Semantic search will be disabled.")

        # Initialiser les services
        self.llm_analyzer = LLMAnalyzer(provider="mistral")  # Mistral par défaut pour le français
        self.doc_scraper = DocumentationScraper(db_manager=db_manager)

        # Initialiser Fast-GraphRAG (avec gestion d'erreur)
        self.fast_graphrag = None
        self.graphrag_enabled = os.getenv("ENABLE_FAST_GRAPHRAG", "true").lower() == "true"
        if self.graphrag_enabled:
            try:
                self.fast_graphrag = FastGraphRAGService()
                self.logger.info("✅ Fast-GraphRAG initialisé avec succès")
            except Exception as e:
                self.logger.warning(f"⚠️ Impossible d'initialiser Fast-GraphRAG: {e}")
                self.logger.warning("⚠️ Fallback vers recherche vectorielle classique")
                self.graphrag_enabled = False

        # Cache pour les embeddings des documents
        self.knowledge_cache = {}
        self.last_cache_update = None

        # Configuration RAG
        self.max_context_documents = 5  # Nombre max de documents à inclure dans le contexte
        self.similarity_threshold = 0.3  # Seuil de similarité minimum
        self.max_context_length = 3000  # Longueur max du contexte en caractères

        # Configuration Fast-GraphRAG
        self.graphrag_timeout = float(os.getenv("GRAPHRAG_TIMEOUT", "5.0"))  # Timeout en secondes
        self.graphrag_min_score = float(os.getenv("GRAPHRAG_MIN_SCORE", "0.5"))  # Score minimum de pertinence

        # Configuration pour l'Agent Agno (création à la demande)
        self.agno_agent = None
        self.agno_available = AGNO_AVAILABLE
        self.llm_provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")

        if self.agno_available:
            self.logger.info(f"🤖 Agno disponible, provider configuré: {self.llm_provider}")
        else:
            self.logger.warning("⚠️ Agno non disponible, utilisation de réponses simulées")
        
        # Prompts système
        self.system_prompts = {
            "default": """Tu es un assistant SAV intelligent pour Free Mobile, l'opérateur télécom français. 
Tu aides les clients avec leurs questions techniques, de facturation, et de service.

INSTRUCTIONS IMPORTANTES:
- Réponds UNIQUEMENT en français
- Sois professionnel, courtois et précis
- Base tes réponses sur la documentation fournie
- Si tu ne connais pas la réponse, dis-le clairement
- Propose des solutions concrètes quand possible
- Évite les informations techniques trop complexes
- Reste dans le domaine du SAV Free Mobile

CONTEXTE DOCUMENTATION:
{context}

HISTORIQUE CONVERSATION:
{conversation_history}""",
            
            "technical": """Tu es un expert technique SAV pour Free Mobile. 
Tu résous les problèmes techniques complexes des clients.

INSTRUCTIONS:
- Fournis des solutions étape par étape
- Explique les procédures clairement
- Demande des précisions si nécessaire
- Propose des alternatives si la première solution ne fonctionne pas

CONTEXTE DOCUMENTATION:
{context}

HISTORIQUE CONVERSATION:
{conversation_history}""",
            
            "billing": """Tu es un spécialiste facturation SAV pour Free Mobile.
Tu aides avec les questions de facturation, abonnements et paiements.

INSTRUCTIONS:
- Explique les tarifs clairement
- Aide avec les problèmes de facturation
- Oriente vers les bonnes procédures
- Reste précis sur les montants et dates

CONTEXTE DOCUMENTATION:
{context}

HISTORIQUE CONVERSATION:
{conversation_history}"""
        }

    def _get_or_create_agno_agent(self):
        """
        Créer un nouvel Agent Agno pour chaque requête
        (Ne pas mettre en cache car le client Ollama n'est pas process-safe avec Gunicorn)

        Returns:
            Agent Agno ou None si non disponible
        """
        # Si Agno n'est pas disponible, retourner None
        if not self.agno_available:
            return None

        try:
            self.logger.info(f"🤖 Création d'un nouvel Agent Agno avec provider: {self.llm_provider}")

            # Créer le modèle selon le provider
            if self.llm_provider == "mistral":
                # Utiliser Mistral API (cloud)
                if self.mistral_api_key and self.mistral_api_key != "test_api_key_for_demo_deployment":
                    model = MistralChat(id="mistral-large-latest", api_key=self.mistral_api_key)
                    self.logger.info("✅ Modèle Mistral API créé")
                else:
                    self.logger.warning("⚠️ MISTRAL_API_KEY non configurée, fallback vers Ollama")
                    self.llm_provider = "ollama"
                    model = Ollama(id="mistral:latest", host=self.ollama_url)
                    self.logger.info(f"✅ Modèle Ollama créé: {self.ollama_url}")
            else:
                # Utiliser Ollama (local)
                model = Ollama(id="mistral:latest", host=self.ollama_url)
                self.logger.info(f"✅ Modèle Ollama créé: {self.ollama_url}")

            # Créer un nouvel Agent Agno pour chaque requête
            agent = Agent(
                name="FreeMobilaChat SAV Agent",
                model=model,
                markdown=True,
                add_history_to_context=False,  # Désactiver pour éviter le warning
                description="Assistant SAV intelligent pour Free Mobile"
            )
            self.logger.info("✅ Agent Agno créé avec succès")

            return agent

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la création de l'Agent Agno: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    async def initialize_knowledge_base(self) -> Dict[str, Any]:
        """
        Initialiser la base de connaissances en scrapant la documentation
        
        Returns:
            Résultat de l'initialisation
        """
        self.logger.info("🚀 Initialisation de la base de connaissances")
        
        try:
            # Mettre à jour la documentation
            result = await self.doc_scraper.update_knowledge_base()
            
            # Recharger le cache
            await self._refresh_knowledge_cache()
            
            self.logger.info("✅ Base de connaissances initialisée")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _refresh_knowledge_cache(self):
        """Recharger le cache des documents de connaissances"""
        try:
            self.logger.info("🔄 Rechargement du cache de connaissances")
            
            # Cette méthode devra être implémentée pour charger depuis la DB
            # Pour l'instant, on simule avec un cache vide
            self.knowledge_cache = {}
            self.last_cache_update = datetime.now(UTC)
            
            self.logger.info("✅ Cache rechargé")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du rechargement du cache: {e}")
    
    async def _search_with_graphrag(self, query: str, max_results: int = 5) -> Optional[List[Tuple[KnowledgeDocument, float]]]:
        """
        Rechercher avec Fast-GraphRAG (méthode principale)

        Args:
            query: Requête de l'utilisateur
            max_results: Nombre maximum de résultats

        Returns:
            Liste de tuples (document, score) ou None si échec/timeout
        """
        if not self.graphrag_enabled or not self.fast_graphrag:
            return None

        try:
            self.logger.info(f"🔍 Recherche Fast-GraphRAG: '{query[:50]}...'")

            # Recherche avec timeout
            graphrag_results = await asyncio.wait_for(
                self.fast_graphrag.query_graph(query, top_k=max_results),
                timeout=self.graphrag_timeout
            )

            # Vérifier la qualité des résultats
            if not graphrag_results:
                self.logger.warning("⚠️ Fast-GraphRAG n'a retourné aucun résultat")
                return None

            # Filtrer par score minimum
            filtered_results = [r for r in graphrag_results if r.get('score', 0) >= self.graphrag_min_score]

            if not filtered_results:
                self.logger.warning(f"⚠️ Aucun résultat Fast-GraphRAG au-dessus du seuil {self.graphrag_min_score}")
                return None

            # Convertir en format KnowledgeDocument
            documents = []
            for result in filtered_results:
                # Créer un document temporaire à partir du résultat GraphRAG
                content = result.get('content', '')
                content_hash = hashlib.sha256(content.encode()).hexdigest()

                doc = KnowledgeDocument(
                    id=result.get('node_id', str(uuid.uuid4())),
                    title=f"GraphRAG Result: {result.get('node_id', 'unknown')}",
                    content=content,
                    document_type='graphrag',
                    source_url='graphrag://internal',
                    source_domain='fast-graphrag',
                    content_hash=content_hash,
                    usage_count=0,
                    relevance_score=result.get('score', 0.0)
                )
                documents.append((doc, result.get('score', 0.0)))

            self.logger.info(f"✅ Fast-GraphRAG: {len(documents)} résultats pertinents")
            return documents

        except asyncio.TimeoutError:
            self.logger.warning(f"⏱️ Timeout Fast-GraphRAG après {self.graphrag_timeout}s")
            return None
        except Exception as e:
            self.logger.error(f"❌ Erreur Fast-GraphRAG: {e}")
            return None

    async def _search_with_vector_db(self, query: str, max_results: int = 5) -> List[Tuple[KnowledgeDocument, float]]:
        """
        Rechercher avec la base de données vectorielle (fallback)

        Args:
            query: Requête de l'utilisateur
            max_results: Nombre maximum de résultats

        Returns:
            Liste de tuples (document, score_similarité)
        """
        try:
            self.logger.info(f"🔍 Recherche vectorielle classique: '{query[:50]}...'")

            # Générer l'embedding de la requête
            query_embedding = self.doc_scraper._generate_embeddings(query)
            if not query_embedding:
                self.logger.warning("⚠️ Impossible de générer l'embedding de la requête")
                return []

            # Rechercher dans la base de données
            if self.db_manager:
                documents_data = await self.db_manager.search_documents_by_embedding(
                    query_embedding, limit=max_results, similarity_threshold=self.similarity_threshold
                )

                # Convertir en format attendu (document, score)
                results = []
                for doc_data in documents_data:
                    # Créer un objet KnowledgeDocument
                    content_hash = doc_data.get('content_hash')
                    if not content_hash or len(content_hash) != 64:
                        content_hash = hashlib.sha256(doc_data['content'].encode()).hexdigest()

                    doc = KnowledgeDocument(
                        id=doc_data['id'],
                        title=doc_data['title'],
                        content=doc_data['content'],
                        document_type=doc_data['document_type'],
                        source_url=doc_data['source_url'],
                        source_domain=doc_data.get('source_domain', 'unknown'),
                        content_hash=content_hash,
                        usage_count=doc_data.get('usage_count', 0),
                        relevance_score=doc_data.get('relevance_score', 0.0)
                    )
                    similarity_score = doc_data.get('similarity_score', 0.8)
                    results.append((doc, similarity_score))

                self.logger.info(f"✅ Recherche vectorielle: {len(results)} documents trouvés")
                return results
            else:
                self.logger.warning("⚠️ Gestionnaire de base de données non disponible")
                return []

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la recherche vectorielle: {e}")
            return []

    async def _search_relevant_documents(self, query: str, max_results: int = 5) -> List[Tuple[KnowledgeDocument, float]]:
        """
        Rechercher les documents les plus pertinents pour une requête
        Utilise Fast-GraphRAG en priorité, avec fallback vers recherche vectorielle

        Args:
            query: Requête de l'utilisateur
            max_results: Nombre maximum de résultats

        Returns:
            Liste de tuples (document, score_similarité)
        """
        # Tentative 1: Fast-GraphRAG
        graphrag_results = await self._search_with_graphrag(query, max_results)

        if graphrag_results:
            self.logger.info(f"✅ Utilisation des résultats Fast-GraphRAG ({len(graphrag_results)} documents)")
            return graphrag_results

        # Fallback: Recherche vectorielle classique
        self.logger.info("🔄 Fallback vers recherche vectorielle classique")
        vector_results = await self._search_with_vector_db(query, max_results)

        return vector_results
    
    def _build_context_from_documents(self, documents: List[Tuple[KnowledgeDocument, float]]) -> str:
        """
        Construire le contexte à partir des documents pertinents
        
        Args:
            documents: Liste de documents avec scores de similarité
            
        Returns:
            Contexte formaté pour le LLM
        """
        if not documents:
            return "Aucune documentation spécifique trouvée pour cette question."
        
        context_parts = []
        total_length = 0
        
        for doc, score in documents:
            if total_length >= self.max_context_length:
                break
            
            # Formater le document
            doc_text = f"[Source: {doc.source_domain}]\n"
            doc_text += f"Titre: {doc.title}\n"
            doc_text += f"Contenu: {doc.content[:800]}...\n"  # Limiter la taille
            doc_text += f"Pertinence: {score:.2f}\n\n"
            
            if total_length + len(doc_text) <= self.max_context_length:
                context_parts.append(doc_text)
                total_length += len(doc_text)
        
        return "\n".join(context_parts)
    
    def _build_conversation_history(self, messages: List[ChatMessage], max_messages: int = 10) -> str:
        """
        Construire l'historique de conversation pour le contexte

        Args:
            messages: Messages de la conversation (peut être des objets ChatMessage ou des dictionnaires)
            max_messages: Nombre maximum de messages à inclure

        Returns:
            Historique formaté
        """
        if not messages:
            return "Début de la conversation."

        # Prendre les derniers messages
        recent_messages = messages[-max_messages:]

        history_parts = []
        for msg in recent_messages:
            # Gérer à la fois les objets ChatMessage et les dictionnaires
            if isinstance(msg, dict):
                role = msg.get('role', 'user')
                content = msg.get('content', '')
            else:
                role = msg.role
                content = msg.content

            role_label = "Client" if role == MessageRole.USER or role == 'user' else "Assistant"
            history_parts.append(f"{role_label}: {content}")

        return "\n".join(history_parts)
    
    def _detect_intent(self, message: str) -> str:
        """
        Détecter l'intention du message pour choisir le bon prompt
        
        Args:
            message: Message de l'utilisateur
            
        Returns:
            Type d'intention détectée
        """
        message_lower = message.lower()
        
        # Mots-clés techniques
        technical_keywords = [
            'problème', 'panne', 'bug', 'erreur', 'ne fonctionne pas',
            'configuration', 'paramétrage', 'installation', 'connexion',
            'réseau', 'wifi', 'data', 'internet', 'signal'
        ]
        
        # Mots-clés facturation
        billing_keywords = [
            'facture', 'facturation', 'paiement', 'prélèvement', 'tarif',
            'abonnement', 'forfait', 'prix', 'coût', 'remboursement',
            'avoir', 'crédit', 'débit'
        ]
        
        if any(keyword in message_lower for keyword in technical_keywords):
            return "technical"
        elif any(keyword in message_lower for keyword in billing_keywords):
            return "billing"
        else:
            return "default"
    
    async def process_message(self, 
                            message: str, 
                            conversation_id: str,
                            llm_provider: str = "mistral",
                            conversation_history: Optional[List[ChatMessage]] = None) -> Dict[str, Any]:
        """
        Traiter un message utilisateur et générer une réponse
        
        Args:
            message: Message de l'utilisateur
            conversation_id: ID de la conversation
            llm_provider: Fournisseur LLM à utiliser
            conversation_history: Historique de la conversation
            
        Returns:
            Réponse avec métadonnées
        """
        start_time = datetime.now(UTC)
        
        try:
            self.logger.info(f"💬 Traitement du message: '{message[:50]}...'")
            
            # Rechercher les documents pertinents
            relevant_docs = await self._search_relevant_documents(message, self.max_context_documents)
            
            # Construire le contexte
            context = self._build_context_from_documents(relevant_docs)
            
            # Construire l'historique
            history = self._build_conversation_history(conversation_history or [])
            
            # Détecter l'intention pour choisir le bon prompt
            intent = self._detect_intent(message)
            
            # Construire le prompt système
            system_prompt = self.system_prompts[intent].format(
                context=context,
                conversation_history=history
            )
            
            # Générer la réponse avec le LLM
            # Pour l'instant, on simule une réponse car l'intégration LLM complète
            # nécessite des ajustements du service existant
            
            response_content = await self._generate_llm_response(
                system_prompt, message, llm_provider
            )
            
            # Calculer le temps de traitement
            processing_time = (datetime.now(UTC) - start_time).total_seconds()
            
            # Extraire les sources utilisées
            sources = [doc.source_url for doc, _ in relevant_docs]

            # Stocker le message utilisateur dans la base de données
            user_message_id = None
            assistant_message_id = None

            self.logger.info(f"🔍 Avant stockage - DB Manager: {self.db_manager}")

            if self.db_manager:
                try:
                    self.logger.info(f"🔍 DB Manager disponible: {self.db_manager is not None}")
                    self.logger.info(f"🔍 DB Type: {self.db_manager.database_type}")

                    # Pour l'instant, nous allons créer une conversation avec un UUID personnalisé
                    # en utilisant le conversation_id comme clé primaire
                    # Extraire session_id du conversation_id (format: conv_{session_id}_{timestamp})
                    # Exemple: conv_test_session_1760744803_20251017_234643 -> test_session_1760744803
                    parts = conversation_id.replace('conv_', '').split('_')
                    if len(parts) >= 3:
                        session_id = '_'.join(parts[:-2])  # Tout sauf les 2 dernières parties (date et heure)
                    else:
                        session_id = conversation_id.replace('conv_', '')

                    # Créer la conversation avec l'ID personnalisé
                    conversation_data = {
                        'id': conversation_id,  # Utiliser l'ID personnalisé
                        'user_id': None,  # Pas d'authentification pour l'instant
                        'session_id': session_id,
                        'title': message[:50] + "..." if len(message) > 50 else message,
                        'status': 'active',
                        'llm_provider': llm_provider,
                        'message_count': 0
                    }

                    self.logger.info(f"📝 Données conversation: {conversation_data}")

                    # Essayer de créer la conversation (ignore si elle existe déjà)
                    created_conv_id = await self.db_manager.store_conversation_with_id(conversation_data)
                    self.logger.info(f"📝 Résultat store_conversation_with_id: {created_conv_id}")
                    if created_conv_id:
                        self.logger.info(f"✅ Conversation créée: {created_conv_id}")
                    else:
                        self.logger.warning(f"⚠️ Impossible de créer la conversation")

                except Exception as conv_error:
                    self.logger.error(f"⚠️ Erreur lors de la gestion de la conversation: {conv_error}", exc_info=True)

                try:
                    # Stocker le message utilisateur
                    user_message_data = {
                        'conversation_id': conversation_id,
                        'role': 'user',
                        'content': message,
                        'sources': [],
                        'llm_provider': None,
                        'processing_time': None
                    }
                    user_message_id = await self.db_manager.store_message(user_message_data)
                    self.logger.info(f"📝 Message utilisateur stocké: {user_message_id}")

                    # Stocker la réponse de l'assistant
                    assistant_message_data = {
                        'conversation_id': conversation_id,
                        'role': 'assistant',
                        'content': response_content,
                        'sources': sources,
                        'llm_provider': llm_provider,
                        'processing_time': processing_time
                    }
                    assistant_message_id = await self.db_manager.store_message(assistant_message_data)
                    self.logger.info(f"📝 Message assistant stocké: {assistant_message_id}")

                except Exception as db_error:
                    self.logger.error(f"⚠️ Erreur lors du stockage des messages: {db_error}", exc_info=True)
            else:
                self.logger.warning(f"⚠️ DB Manager non disponible")

            result = {
                'success': True,
                'response': response_content,
                'sources': sources,
                'processing_time': processing_time,
                'llm_provider': llm_provider,
                'intent_detected': intent,
                'documents_found': len(relevant_docs),
                'conversation_id': conversation_id,
                'message_id': assistant_message_id  # ID du message assistant pour le feedback
            }

            self.logger.info(f"✅ Réponse générée en {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du traitement: {e}")
            return {
                'success': False,
                'error': str(e),
                'conversation_id': conversation_id,
                'processing_time': (datetime.now(UTC) - start_time).total_seconds()
            }
    
    async def _generate_llm_response(self, system_prompt: str, user_message: str, provider: str) -> str:
        """
        Générer une réponse avec le LLM via l'Agent Agno

        Args:
            system_prompt: Prompt système avec contexte
            user_message: Message utilisateur
            provider: Fournisseur LLM

        Returns:
            Réponse générée
        """
        try:
            # Obtenir ou créer l'Agent Agno
            agent = self._get_or_create_agno_agent()

            # Utiliser l'Agent Agno si disponible
            if agent:
                self.logger.info(f"🤖 Génération de réponse avec Agent Agno pour: {user_message[:50]}...")

                # Construire le message complet avec le contexte système
                full_message = f"{system_prompt}\n\nQUESTION CLIENT:\n{user_message}"

                # Générer la réponse avec l'Agent Agno (appel synchrone dans un contexte async)
                import asyncio
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, agent.run, full_message)

                # Extraire le contenu de la réponse
                if hasattr(response, 'content'):
                    response_text = response.content
                elif isinstance(response, str):
                    response_text = response
                else:
                    response_text = str(response)

                self.logger.info(f"✅ Réponse générée avec succès ({len(response_text)} caractères)")
                return response_text

            # Fallback: réponse simulée si Agno non disponible
            self.logger.warning("⚠️ Agent Agno non disponible, utilisation de réponse simulée")
            response = f"""Bonjour ! Je suis votre assistant SAV Free Mobile.

J'ai bien reçu votre message : "{user_message}"

Je suis en cours de développement et bientôt je pourrai vous aider avec :
- Vos questions techniques sur votre mobile Free
- Vos problèmes de facturation et d'abonnement
- La configuration de vos services
- Le dépannage de votre ligne

En attendant, je vous invite à consulter notre documentation sur assistance.free.fr ou à contacter notre service client au 3244.

Comment puis-je vous aider davantage ?"""

            return response

        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la génération LLM: {e}")
            self.logger.error(f"❌ Type d'erreur: {type(e).__name__}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

            # Fallback en cas d'erreur
            return "Désolé, je rencontre actuellement des difficultés techniques. Veuillez réessayer dans quelques instants."
