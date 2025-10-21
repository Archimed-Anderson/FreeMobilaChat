#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script pour valider les fonctionnalités de base de données du chatbot
"""

import asyncio
import json
import requests
import time
from datetime import datetime
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BASE_URL = "http://localhost:8000"
SESSION_ID = f"test_session_{int(time.time())}"

def test_api_health():
    """Test de l'API health"""
    print("🔍 Test de l'API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(" API health OK")
            return True
        else:
            print(f" API health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f" Erreur API health: {e}")
        return False

def test_chatbot_message():
    """Test d'envoi de message au chatbot"""
    print("\n💬 Test d'envoi de message au chatbot...")
    try:
        payload = {
            "message": "Bonjour, j'ai un problème avec ma facture Free Mobile",
            "session_id": SESSION_ID,
            "llm_provider": "mistral"
        }
        
        response = requests.post(f"{BASE_URL}/api/chatbot/message", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(" Message envoyé avec succès")
            print(f"   - Conversation ID: {data.get('conversation_id')}")
            print(f"   - Message ID: {data.get('message_id')}")
            print(f"   - Temps de traitement: {data.get('processing_time'):.2f}s")
            print(f"   - Documents trouvés: {data.get('documents_found')}")
            print(f"   - Réponse: {data.get('response', '')[:100]}...")
            return data.get('conversation_id'), data.get('message_id')
        else:
            print(f" Erreur envoi message: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None, None
            
    except Exception as e:
        print(f" Erreur test message: {e}")
        return None, None

def test_get_conversations():
    """Test de récupération des conversations"""
    print("\n📋 Test de récupération des conversations...")
    try:
        response = requests.get(f"{BASE_URL}/api/chatbot/conversations/test_user")

        if response.status_code == 200:
            data = response.json()
            conversations = data.get('conversations', [])
            print(f" Conversations récupérées: {len(conversations)} trouvées")
            for conv in conversations[:3]:  # Afficher les 3 premières
                print(f"   - ID: {conv.get('id')}")
                print(f"   - Titre: {conv.get('title', 'Sans titre')}")
                print(f"   - Messages: {conv.get('message_count', 0)}")
                print(f"   - Statut: {conv.get('status')}")
            return True
        else:
            print(f" Erreur récupération conversations: {response.status_code}")
            return False

    except Exception as e:
        print(f" Erreur test conversations: {e}")
        return False

def test_feedback(conversation_id, message_id):
    """Test d'envoi de feedback"""
    print("\n Test d'envoi de feedback...")
    try:
        if not conversation_id or not message_id:
            print(" Pas de conversation/message ID, skip du test feedback")
            return False
            
        payload = {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "feedback_type": "thumbs_up",
            "rating": 4,
            "comment": "Réponse utile, merci !",
            "session_id": SESSION_ID
        }
        
        response = requests.post(f"{BASE_URL}/api/chatbot/feedback", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(" Feedback envoyé avec succès")
            print(f"   - Feedback ID: {data.get('feedback_id')}")
            return True
        else:
            print(f" Erreur envoi feedback: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f" Erreur test feedback: {e}")
        return False

def test_initialize_chatbot():
    """Test d'initialisation du chatbot"""
    print("\n Test d'initialisation du chatbot...")
    try:
        response = requests.post(f"{BASE_URL}/api/chatbot/initialize")
        
        if response.status_code == 200:
            data = response.json()
            print(" Initialisation réussie")
            print(f"   - Documents traités: {data.get('documents_processed', 0)}")
            print(f"   - Temps total: {data.get('total_time', 0):.2f}s")
            return True
        else:
            print(f" Erreur initialisation: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f" Erreur test initialisation: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TESTS DE LA BASE DE DONNÉES CHATBOT")
    print("=" * 50)
    
    results = []
    
    # Test 1: API Health
    results.append(test_api_health())
    
    # Test 2: Envoi de message
    conversation_id, message_id = test_chatbot_message()
    results.append(conversation_id is not None)
    
    # Test 3: Récupération des conversations
    results.append(test_get_conversations())
    
    # Test 4: Envoi de feedback
    results.append(test_feedback(conversation_id, message_id))
    
    # Test 5: Initialisation du chatbot
    results.append(test_initialize_chatbot())
    
    # Résumé
    print("\n" + "=" * 50)
    print(" RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    test_names = [
        "API Health",
        "Envoi de message",
        "Récupération conversations", 
        "Envoi de feedback",
        "Initialisation chatbot"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = " PASS" if result else " FAIL"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n RÉSULTAT FINAL: {passed}/{total} tests réussis")
    
    if passed == total:
        print(" Tous les tests sont passés ! La base de données du chatbot est opérationnelle.")
    else:
        print(" Certains tests ont échoué. Vérifiez les logs ci-dessus.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
