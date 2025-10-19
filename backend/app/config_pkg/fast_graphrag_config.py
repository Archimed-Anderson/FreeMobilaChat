"""
Configuration pour Fast-GraphRAG
Intégration du système de graphe de connaissances pour améliorer la récupération de contexte (RAG)
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class FastGraphRAGConfig:
    """Configuration pour Fast-GraphRAG"""
    
    # Modèle d'embedding (réutiliser le modèle multilingue existant)
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384  # Dimension des embeddings pour ce modèle
    
    # Configuration LLM pour l'extraction d'entités (Ollama/Mistral)
    llm_provider: str = "ollama"
    llm_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    llm_model: str = "mistral:latest"
    llm_temperature: float = 0.1  # Température basse pour extraction d'entités précise
    
    # Paramètres du graphe
    max_graph_nodes: int = 1000  # Nombre maximum de nœuds dans le graphe
    max_graph_depth: int = 3  # Profondeur maximale de traversée du graphe
    similarity_threshold: float = 0.5  # Seuil de similarité pour créer des liens (réduit pour plus de résultats)
    min_entity_frequency: int = 2  # Fréquence minimale pour considérer une entité
    
    # Paramètres de récupération
    top_k_nodes: int = 5  # Nombre de nœuds à récupérer lors d'une requête
    top_k_edges: int = 10  # Nombre d'arêtes à considérer
    use_pagerank: bool = True  # Utiliser PageRank pour le classement des nœuds
    pagerank_iterations: int = 20  # Nombre d'itérations PageRank
    
    # Chemins de stockage
    storage_dir: Path = Path("/app/data/fast_graphrag")
    graph_file: str = "knowledge_graph.pkl"
    index_file: str = "vector_index.bin"
    metadata_file: str = "graph_metadata.json"
    
    # Paramètres de performance
    batch_size: int = 32  # Taille de batch pour le traitement
    max_workers: int = 4  # Nombre de workers pour le traitement parallèle
    cache_embeddings: bool = True  # Mettre en cache les embeddings
    
    # Paramètres de mise à jour incrémentale
    enable_incremental_updates: bool = True
    update_threshold: int = 10  # Nombre de documents avant mise à jour du graphe
    
    # Fallback configuration
    enable_fallback: bool = True  # Activer le fallback vers recherche vectorielle simple
    fallback_on_error: bool = True  # Fallback automatique en cas d'erreur
    
    def __post_init__(self):
        """Créer les répertoires de stockage si nécessaire"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def graph_path(self) -> Path:
        """Chemin complet vers le fichier de graphe"""
        return self.storage_dir / self.graph_file
    
    @property
    def index_path(self) -> Path:
        """Chemin complet vers le fichier d'index"""
        return self.storage_dir / self.index_file
    
    @property
    def metadata_path(self) -> Path:
        """Chemin complet vers le fichier de métadonnées"""
        return self.storage_dir / self.metadata_file


# Instance globale de configuration
config = FastGraphRAGConfig()


def get_config() -> FastGraphRAGConfig:
    """Récupérer la configuration Fast-GraphRAG"""
    return config


def update_config(**kwargs) -> FastGraphRAGConfig:
    """
    Mettre à jour la configuration Fast-GraphRAG
    
    Args:
        **kwargs: Paramètres de configuration à mettre à jour
        
    Returns:
        Configuration mise à jour
    """
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config

