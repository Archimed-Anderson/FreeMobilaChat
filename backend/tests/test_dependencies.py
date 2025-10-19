#!/usr/bin/env python3
"""
Script de test des dépendances du chatbot FreeMobilaChat
Phase 2.1 - Vérification des imports après installation
"""

import sys
import traceback
from typing import List, Tuple

def test_import(module_name: str, description: str) -> Tuple[bool, str]:
    """Test l'import d'un module et retourne le résultat."""
    try:
        __import__(module_name)
        return True, f"✅ {description}"
    except ImportError as e:
        return False, f"❌ {description} - Erreur: {str(e)}"
    except Exception as e:
        return False, f"⚠️ {description} - Erreur inattendue: {str(e)}"

def test_specific_imports() -> List[Tuple[bool, str]]:
    """Test des imports spécifiques pour le chatbot."""
    results = []
    
    # Test des dépendances de base
    results.append(test_import("requests", "HTTP Client (requests)"))
    results.append(test_import("bs4", "HTML Parser (beautifulsoup4)"))
    results.append(test_import("streamlit_chat", "Interface Chat (streamlit-chat)"))
    
    # Test de sentence-transformers (le plus lourd)
    try:
        from sentence_transformers import SentenceTransformer
        results.append((True, "✅ Embeddings (sentence-transformers) - Import réussi"))
        
        # Test de création d'un modèle
        try:
            model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            results.append((True, "✅ Modèle multilingue - Chargement réussi"))
        except Exception as e:
            results.append((False, f"⚠️ Modèle multilingue - Erreur de chargement: {str(e)}"))
            
    except ImportError as e:
        results.append((False, f"❌ Embeddings (sentence-transformers) - Erreur: {str(e)}"))
    except Exception as e:
        results.append((False, f"⚠️ Embeddings (sentence-transformers) - Erreur inattendue: {str(e)}"))
    
    # Test des dépendances scientifiques
    results.append(test_import("numpy", "Calculs vectoriels (numpy)"))
    results.append(test_import("sklearn", "Machine Learning (scikit-learn)"))
    
    return results

def test_chatbot_services() -> List[Tuple[bool, str]]:
    """Test des services chatbot."""
    results = []
    
    try:
        from app.services.documentation_scraper import DocumentationScraper
        results.append((True, "✅ DocumentationScraper - Import réussi"))
        
        # Test d'instanciation
        try:
            scraper = DocumentationScraper()
            results.append((True, "✅ DocumentationScraper - Instanciation réussie"))
        except Exception as e:
            results.append((False, f"⚠️ DocumentationScraper - Erreur d'instanciation: {str(e)}"))
            
    except ImportError as e:
        results.append((False, f"❌ DocumentationScraper - Erreur d'import: {str(e)}"))
    
    try:
        from app.services.chatbot_service import ChatbotService
        results.append((True, "✅ ChatbotService - Import réussi"))
        
        # Test d'instanciation
        try:
            chatbot = ChatbotService()
            results.append((True, "✅ ChatbotService - Instanciation réussie"))
        except Exception as e:
            results.append((False, f"⚠️ ChatbotService - Erreur d'instanciation: {str(e)}"))
            
    except ImportError as e:
        results.append((False, f"❌ ChatbotService - Erreur d'import: {str(e)}"))
    
    return results

def main():
    """Fonction principale de test."""
    print("🧪 TEST DES DÉPENDANCES CHATBOT FREEMOBILACHAT")
    print("=" * 60)
    
    # Test des imports de base
    print("\n📦 DÉPENDANCES DE BASE:")
    basic_results = test_specific_imports()
    for success, message in basic_results:
        print(f"  {message}")
    
    # Test des services chatbot
    print("\n🤖 SERVICES CHATBOT:")
    service_results = test_chatbot_services()
    for success, message in service_results:
        print(f"  {message}")
    
    # Résumé
    all_results = basic_results + service_results
    success_count = sum(1 for success, _ in all_results if success)
    total_count = len(all_results)
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSUMÉ: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("🎉 Tous les tests sont passés ! Le chatbot est prêt.")
        return 0
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
