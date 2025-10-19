"""
Service Fast-GraphRAG pour la récupération de contexte basée sur un graphe de connaissances
Améliore la qualité du RAG en utilisant des relations sémantiques entre les entités
"""

import logging
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import asyncio

from app.config_pkg.fast_graphrag_config import get_config, FastGraphRAGConfig

# Configuration du logger
logger = logging.getLogger(__name__)


class FastGraphRAGService:
    """
    Service de récupération de contexte basé sur Fast-GraphRAG
    Utilise un graphe de connaissances pour améliorer la qualité du RAG
    """
    
    def __init__(self, config: Optional[FastGraphRAGConfig] = None):
        """
        Initialiser le service Fast-GraphRAG
        
        Args:
            config: Configuration Fast-GraphRAG (utilise la config par défaut si None)
        """
        self.config = config or get_config()
        self.graph = None
        self.embedding_model = None
        self.is_initialized = False
        
        logger.info("🚀 Initialisation du service Fast-GraphRAG")
        logger.info(f"   - Modèle d'embedding: {self.config.embedding_model}")
        logger.info(f"   - LLM Provider: {self.config.llm_provider}")
        logger.info(f"   - Stockage: {self.config.storage_dir}")
        
        # Initialiser de manière asynchrone
        try:
            self._initialize()
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation Fast-GraphRAG: {e}")
            if not self.config.fallback_on_error:
                raise
    
    def _initialize(self):
        """Initialiser les composants Fast-GraphRAG"""
        try:
            # Importer Fast-GraphRAG (import tardif pour éviter les erreurs au démarrage)
            from fast_graphrag import GraphRAG
            from sentence_transformers import SentenceTransformer
            
            # Charger le modèle d'embedding
            logger.info(f"📦 Chargement du modèle d'embedding: {self.config.embedding_model}")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            
            # Initialiser ou charger le graphe existant
            if self.config.graph_path.exists():
                logger.info(f"📂 Chargement du graphe existant depuis {self.config.graph_path}")
                self.graph = self._load_graph()
            else:
                logger.info("🆕 Création d'un nouveau graphe de connaissances")
                self.graph = self._create_new_graph()
            
            self.is_initialized = True
            logger.info("✅ Service Fast-GraphRAG initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation des composants: {e}")
            self.is_initialized = False
            if not self.config.fallback_on_error:
                raise
    
    def _create_new_graph(self) -> Any:
        """
        Créer un nouveau graphe de connaissances
        
        Returns:
            Instance du graphe
        """
        # Pour l'instant, retourner un dictionnaire simple
        # TODO: Implémenter avec Fast-GraphRAG une fois la structure définie
        return {
            "nodes": {},
            "edges": [],
            "metadata": {
                "created_at": str(Path(__file__).stat().st_mtime),
                "num_documents": 0
            }
        }
    
    def _load_graph(self) -> Any:
        """
        Charger un graphe existant depuis le disque
        
        Returns:
            Instance du graphe chargé
        """
        try:
            with open(self.config.graph_path, 'rb') as f:
                graph = pickle.load(f)
            logger.info(f"✅ Graphe chargé: {graph.get('metadata', {}).get('num_documents', 0)} documents")
            return graph
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du graphe: {e}")
            return self._create_new_graph()
    
    def _save_graph(self):
        """Sauvegarder le graphe sur le disque"""
        try:
            with open(self.config.graph_path, 'wb') as f:
                pickle.dump(self.graph, f)
            logger.info(f"💾 Graphe sauvegardé dans {self.config.graph_path}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde du graphe: {e}")
    
    async def build_graph_from_documents(self, documents: List[str]) -> bool:
        """
        Construire le graphe de connaissances à partir de documents
        
        Args:
            documents: Liste de documents textuels
            
        Returns:
            True si succès, False sinon
        """
        if not self.is_initialized:
            logger.warning("⚠️ Service non initialisé, tentative de réinitialisation")
            self._initialize()
            if not self.is_initialized:
                logger.error("❌ Impossible d'initialiser le service")
                return False
        
        try:
            logger.info(f"🔨 Construction du graphe à partir de {len(documents)} documents")
            
            # TODO: Implémenter la construction du graphe avec Fast-GraphRAG
            # Pour l'instant, stocker simplement les documents
            if self.graph is None:
                self.graph = self._create_new_graph()
            
            for idx, doc in enumerate(documents):
                node_id = f"doc_{idx}"
                self.graph["nodes"][node_id] = {
                    "content": doc,
                    "embedding": self.embedding_model.encode(doc).tolist()
                }
            
            self.graph["metadata"]["num_documents"] = len(documents)
            self._save_graph()
            
            logger.info(f"✅ Graphe construit avec succès: {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la construction du graphe: {e}")
            return False
    
    async def query_graph(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Interroger le graphe pour récupérer le contexte pertinent
        
        Args:
            query: Requête utilisateur
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de contextes pertinents avec leurs scores
        """
        if not self.is_initialized or self.graph is None:
            logger.warning("⚠️ Graphe non disponible, retour d'une liste vide")
            return []
        
        try:
            logger.info(f"🔍 Recherche dans le graphe: '{query[:50]}...'")
            
            # Encoder la requête
            query_embedding = self.embedding_model.encode(query)
            
            # TODO: Implémenter la recherche avec Fast-GraphRAG et PageRank
            # Pour l'instant, recherche vectorielle simple
            results = []
            for node_id, node_data in self.graph["nodes"].items():
                # Calculer la similarité cosinus
                import numpy as np
                node_emb = np.array(node_data["embedding"])
                similarity = np.dot(query_embedding, node_emb) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(node_emb)
                )
                
                if similarity >= self.config.similarity_threshold:
                    results.append({
                        "content": node_data["content"],
                        "score": float(similarity),
                        "node_id": node_id
                    })
            
            # Trier par score et retourner top_k
            results.sort(key=lambda x: x["score"], reverse=True)
            results = results[:top_k]
            
            logger.info(f"✅ Trouvé {len(results)} résultats pertinents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche dans le graphe: {e}")
            return []
    
    async def update_graph(self, new_documents: List[str]) -> bool:
        """
        Mise à jour incrémentale du graphe avec de nouveaux documents
        
        Args:
            new_documents: Liste de nouveaux documents à ajouter
            
        Returns:
            True si succès, False sinon
        """
        if not self.config.enable_incremental_updates:
            logger.info("⚠️ Mises à jour incrémentales désactivées")
            return False
        
        try:
            logger.info(f"🔄 Mise à jour incrémentale: {len(new_documents)} nouveaux documents")
            
            # Ajouter les nouveaux documents au graphe existant
            if self.graph is None:
                return await self.build_graph_from_documents(new_documents)
            
            current_num_docs = self.graph["metadata"]["num_documents"]
            
            for idx, doc in enumerate(new_documents):
                node_id = f"doc_{current_num_docs + idx}"
                self.graph["nodes"][node_id] = {
                    "content": doc,
                    "embedding": self.embedding_model.encode(doc).tolist()
                }
            
            self.graph["metadata"]["num_documents"] += len(new_documents)
            self._save_graph()
            
            logger.info(f"✅ Graphe mis à jour: {self.graph['metadata']['num_documents']} documents au total")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour du graphe: {e}")
            return False
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Obtenir les statistiques du graphe
        
        Returns:
            Dictionnaire avec les statistiques
        """
        if self.graph is None:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized" if self.is_initialized else "error",
            "num_nodes": len(self.graph.get("nodes", {})),
            "num_edges": len(self.graph.get("edges", [])),
            "num_documents": self.graph.get("metadata", {}).get("num_documents", 0),
            "storage_path": str(self.config.graph_path)
        }

