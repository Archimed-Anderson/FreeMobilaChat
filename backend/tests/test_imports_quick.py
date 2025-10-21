#!/usr/bin/env python3
"""
Script de test rapide pour vérifier les imports des dépendances chatbot
après le build Docker.
"""

import sys
import time
from typing import List, Tuple

def test_import(module_name: str, description: str) -> Tuple[bool, str]:
    """Test l'import d'un module et retourne le résultat."""
    try:
        start_time = time.time()
        __import__(module_name)
        end_time = time.time()
        duration = end_time - start_time
        return True, f" {description} ({duration:.2f}s)"
    except ImportError as e:
        return False, f" {description} - Erreur: {str(e)}"
    except Exception as e:
        return False, f" {description} - Erreur inattendue: {str(e)}"

def test_basic_imports() -> List[Tuple[bool, str]]:
    """Test des imports de base."""
    results = []
    
    # Dépendances de base
    basic_deps = [
        ("requests", "HTTP Client (requests)"),
        ("bs4", "HTML Parser (beautifulsoup4)"),
        ("streamlit_chat", "Interface Chat (streamlit-chat)"),
        ("aiohttp", "HTTP Client Async (aiohttp)"),
        ("numpy", "Calculs numériques (numpy)"),
        ("sklearn", "Machine Learning (scikit-learn)")
    ]
    
    for module, desc in basic_deps:
        results.append(test_import(module, desc))
    
    return results

def test_sentence_transformers() -> List[Tuple[bool, str]]:
    """Test spécifique pour sentence-transformers (le plus lourd)."""
    results = []
    
    # Test d'import de base
    try:
        start_time = time.time()
        from sentence_transformers import SentenceTransformer
        end_time = time.time()
        duration = end_time - start_time
        results.append((True, f" Embeddings (sentence-transformers) - Import réussi ({duration:.2f}s)"))
        
        # Test de création d'un modèle (plus lourd)
        try:
            start_time = time.time()
            model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            end_time = time.time()
            duration = end_time - start_time
            results.append((True, f" Modèle multilingue - Chargement réussi ({duration:.2f}s)"))
            
            # Test d'encoding rapide
            try:
                start_time = time.time()
                embeddings = model.encode(["Test de fonctionnement"])
                end_time = time.time()
                duration = end_time - start_time
                results.append((True, f" Encoding de test - Fonctionnel ({duration:.2f}s, dim={len(embeddings[0])})"))
            except Exception as e:
                results.append((False, f" Encoding de test - Erreur: {str(e)}"))
                
        except Exception as e:
            results.append((False, f" Modèle multilingue - Erreur de chargement: {str(e)}"))
            
    except ImportError as e:
        results.append((False, f" Embeddings (sentence-transformers) - Erreur: {str(e)}"))
    except Exception as e:
        results.append((False, f" Embeddings (sentence-transformers) - Erreur inattendue: {str(e)}"))
    
    return results

def test_chatbot_services() -> List[Tuple[bool, str]]:
    """Test des services chatbot."""
    results = []
    
    try:
        from app.services.documentation_scraper import DocumentationScraper
        results.append((True, " DocumentationScraper - Import réussi"))
    except Exception as e:
        results.append((False, f" DocumentationScraper - Erreur: {str(e)}"))
    
    try:
        from app.services.chatbot_service import ChatbotService
        results.append((True, " ChatbotService - Import réussi"))
    except Exception as e:
        results.append((False, f" ChatbotService - Erreur: {str(e)}"))
    
    try:
        from app.models import ChatMessage, Conversation, KnowledgeDocument, ChatFeedback
        results.append((True, " Modèles Chatbot - Import réussi"))
    except Exception as e:
        results.append((False, f" Modèles Chatbot - Erreur: {str(e)}"))
    
    return results

def main():
    """Fonction principale de test."""
    print("🧪 TEST RAPIDE DES DÉPENDANCES CHATBOT")
    print("=" * 50)
    
    total_start_time = time.time()
    
    # Test des imports de base
    print("\n📦 DÉPENDANCES DE BASE:")
    basic_results = test_basic_imports()
    for success, message in basic_results:
        print(f"  {message}")
    
    # Test de sentence-transformers
    print("\n🤖 SENTENCE TRANSFORMERS:")
    st_results = test_sentence_transformers()
    for success, message in st_results:
        print(f"  {message}")
    
    # Test des services chatbot
    print("\n💬 SERVICES CHATBOT:")
    service_results = test_chatbot_services()
    for success, message in service_results:
        print(f"  {message}")
    
    # Résumé
    all_results = basic_results + st_results + service_results
    success_count = sum(1 for success, _ in all_results if success)
    total_count = len(all_results)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    print("\n" + "=" * 50)
    print(f" RÉSUMÉ: {success_count}/{total_count} tests réussis")
    print(f"⏱ DURÉE TOTALE: {total_duration:.2f}s")
    
    if success_count == total_count:
        print(" TOUS LES TESTS SONT RÉUSSIS!")
        sys.exit(0)
    else:
        print(" CERTAINS TESTS ONT ÉCHOUÉ")
        sys.exit(1)

if __name__ == "__main__":
    main()
