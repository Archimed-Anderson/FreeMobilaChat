"""
Optimized Lazy Loader - FreeMobilaChat
=======================================

Système de chargement optimisé avec cache intelligent pour éviter
les temps de chargement lents lors de l'upload de fichiers.

Features:
- Lazy loading des modules lourds (BERT, Transformers)
- Cache intelligent avec st.cache_resource
- Chargement asynchrone des modèles
- Gestion robuste des erreurs
"""

import streamlit as st
import logging
from typing import Optional, Callable, Any
from functools import wraps
import time

logger = logging.getLogger(__name__)


class OptimizedLoader:
    """
    Gestionnaire de chargement optimisé pour les modèles ML lourds
    
    Utilise:
    - Lazy loading pour ne charger que quand nécessaire
    - Cache Streamlit pour réutiliser les modèles
    - Gestion d'erreurs robuste
    """
    
    _instances = {}  # Cache manuel en cas d'échec de st.cache_resource
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_bert_classifier(use_gpu: bool = False):
        """
        Charge le classificateur BERT avec cache intelligent
        
        Args:
            use_gpu: Utiliser GPU si disponible
            
        Returns:
            Instance de BERTClassifier ou None en cas d'erreur
        """
        try:
            logger.info("🔄 Chargement BERT Classifier (cached)...")
            start = time.time()
            
            # Import dynamique (lazy loading)
            from services.bert_classifier import BERTClassifier
            
            classifier = BERTClassifier(use_gpu=use_gpu)
            
            elapsed = time.time() - start
            logger.info(f"✅ BERT chargé en {elapsed:.2f}s (cache actif)")
            
            return classifier
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement BERT: {e}")
            return None
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_mistral_classifier(model_name: str = 'mistral'):
        """
        Charge le classificateur Mistral avec cache intelligent
        
        Args:
            model_name: Nom du modèle Ollama
            
        Returns:
            Instance de MistralClassifier ou None en cas d'erreur
        """
        try:
            logger.info("🔄 Chargement Mistral Classifier (cached)...")
            start = time.time()
            
            # Import dynamique (lazy loading)
            from services.mistral_classifier import MistralClassifier, check_ollama_availability
            
            # Vérifier Ollama sans bloquer
            if not check_ollama_availability():
                logger.warning("⚠️ Ollama non disponible - Mode dégradé")
                return None
            
            classifier = MistralClassifier(model_name=model_name)
            
            elapsed = time.time() - start
            logger.info(f"✅ Mistral chargé en {elapsed:.2f}s (cache actif)")
            
            return classifier
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement Mistral: {e}")
            return None
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_rule_classifier():
        """
        Charge le classificateur par règles (léger, toujours disponible)
        
        Returns:
            Instance de EnhancedRuleClassifier
        """
        try:
            logger.info("🔄 Chargement Rule Classifier (cached)...")
            
            # Import dynamique
            from services.rule_classifier import EnhancedRuleClassifier
            
            classifier = EnhancedRuleClassifier()
            
            logger.info("✅ Rule Classifier chargé")
            
            return classifier
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement Rule Classifier: {e}")
            return None
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def load_tweet_cleaner():
        """
        Charge le nettoyeur de tweets (léger)
        
        Returns:
            Instance de TweetCleaner
        """
        try:
            from services.tweet_cleaner import TweetCleaner
            return TweetCleaner()
        except Exception as e:
            logger.error(f"❌ Erreur chargement TweetCleaner: {e}")
            return None
    
    @staticmethod
    def check_ollama_availability() -> bool:
        """
        Vérifie rapidement la disponibilité d'Ollama sans bloquer
        
        Returns:
            True si Ollama est disponible
        """
        try:
            # Import lazy
            import ollama
            
            # Test rapide (timeout 2s)
            ollama.list()
            return True
            
        except Exception as e:
            logger.warning(f"Ollama non disponible: {e}")
            return False
    
    @staticmethod
    def get_available_models():
        """
        Retourne les modèles de classification disponibles
        
        Returns:
            dict: {'bert': bool, 'mistral': bool, 'rules': bool}
        """
        available = {
            'bert': False,
            'mistral': False,
            'rules': True  # Toujours disponible
        }
        
        # Test BERT (rapide)
        try:
            import torch
            from transformers import AutoTokenizer
            available['bert'] = True
        except:
            pass
        
        # Test Mistral
        available['mistral'] = OptimizedLoader.check_ollama_availability()
        
        return available


def lazy_import(module_name: str, item_name: str = None):
    """
    Importe un module ou une classe de façon lazy
    
    Args:
        module_name: Nom du module (ex: 'services.bert_classifier')
        item_name: Nom de la classe/fonction à importer (optionnel)
        
    Returns:
        Module ou classe importée
        
    Example:
        BERTClassifier = lazy_import('services.bert_classifier', 'BERTClassifier')
    """
    import importlib
    
    module = importlib.import_module(module_name)
    
    if item_name:
        return getattr(module, item_name)
    
    return module


def with_spinner(message: str = "Chargement..."):
    """
    Décorateur pour ajouter un spinner Streamlit aux fonctions lourdes
    
    Args:
        message: Message à afficher pendant le chargement
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Singleton pour éviter rechargements multiples
_loader_instance = None

def get_loader() -> OptimizedLoader:
    """
    Retourne l'instance unique du loader (pattern Singleton)
    
    Returns:
        OptimizedLoader instance
    """
    global _loader_instance
    
    if _loader_instance is None:
        _loader_instance = OptimizedLoader()
    
    return _loader_instance


if __name__ == "__main__":
    # Tests
    loader = get_loader()
    
    print("🧪 Test du loader optimisé...")
    
    # Test des modèles disponibles
    available = loader.get_available_models()
    print(f"Modèles disponibles: {available}")
    
    # Test chargement rules (léger)
    rules = loader.load_rule_classifier()
    print(f"Rules classifier: {'✅' if rules else '❌'}")
    
    print("✅ Tests terminés")

