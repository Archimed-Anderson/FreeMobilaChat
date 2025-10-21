"""
Script de test pour l'API Chatbot FreeMobilaChat
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Tester l'endpoint de santé"""
    print("🔍 Test de l'endpoint de santé...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(" API en ligne")
            return True
        else:
            print(f" API répond avec le statut {response.status_code}")
            return False
    except Exception as e:
        print(f" Erreur de connexion à l'API: {e}")
        return False

def test_chatbot_message():
    """Tester l'endpoint de message du chatbot"""
    print("\n💬 Test de l'endpoint chatbot message...")
    
    payload = {
        "message": "Bonjour, j'ai un problème avec mon téléphone Free Mobile",
        "session_id": "test_session_123",
        "llm_provider": "mistral"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chatbot/message",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(" Endpoint chatbot fonctionne")
            print(f"   - Succès: {result.get('success')}")
            print(f"   - Réponse: {result.get('response', '')[:100]}...")
            print(f"   - Temps de traitement: {result.get('processing_time', 0):.2f}s")
            print(f"   - Conversation ID: {result.get('conversation_id')}")
            return True
        else:
            print(f" Erreur HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Détail: {error_detail}")
            except:
                print(f"   Contenu: {response.text}")
            return False
            
    except Exception as e:
        print(f" Erreur lors du test: {e}")
        return False

def test_chatbot_initialize():
    """Tester l'endpoint d'initialisation du chatbot"""
    print("\n Test de l'endpoint d'initialisation...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chatbot/initialize",
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(" Endpoint d'initialisation fonctionne")
            print(f"   - Succès: {result.get('success')}")
            if result.get('success'):
                print(f"   - Documents scrapés: {result.get('successful_scrapes', 0)}")
                print(f"   - Durée: {result.get('duration_seconds', 0):.1f}s")
            else:
                print(f"   - Erreur: {result.get('error')}")
            return True
        else:
            print(f" Erreur HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Détail: {error_detail}")
            except:
                print(f"   Contenu: {response.text}")
            return False
            
    except Exception as e:
        print(f" Erreur lors du test: {e}")
        return False

def test_conversations_endpoint():
    """Tester l'endpoint de récupération des conversations"""
    print("\n📋 Test de l'endpoint conversations...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/chatbot/conversations/test_user",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(" Endpoint conversations fonctionne")
            print(f"   - Succès: {result.get('success')}")
            print(f"   - Nombre de conversations: {result.get('total', 0)}")
            return True
        else:
            print(f" Erreur HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f" Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TESTS API CHATBOT FREEMOBILACHAT")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Santé de l'API
    if test_health():
        tests_passed += 1
    
    # Test 2: Message chatbot
    if test_chatbot_message():
        tests_passed += 1
    
    # Test 3: Initialisation
    if test_chatbot_initialize():
        tests_passed += 1
    
    # Test 4: Conversations
    if test_conversations_endpoint():
        tests_passed += 1
    
    # Résumé
    print("\n" + "=" * 50)
    print(f" RÉSUMÉ: {tests_passed}/{total_tests} tests réussis")
    
    if tests_passed == total_tests:
        print(" Tous les tests sont passés ! L'API chatbot est fonctionnelle.")
    else:
        print(" Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()
