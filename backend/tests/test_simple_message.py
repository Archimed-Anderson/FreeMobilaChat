#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple pour envoyer un message au chatbot
"""

import requests
import json
import time
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BASE_URL = "http://localhost:8000"
SESSION_ID = f"test_session_{int(time.time())}"

def test_simple_message():
    """Test simple d'envoi de message"""
    print("💬 Test d'envoi de message au chatbot...")
    
    payload = {
        "message": "Bonjour, j'ai un problème avec ma facture Free Mobile",
        "session_id": SESSION_ID,
        "llm_provider": "mistral"
    }
    
    try:
        print(f"Envoi vers: {BASE_URL}/api/chatbot/message")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/chatbot/message", 
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(" Réponse reçue:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f" Erreur: {response.status_code}")
            print(f"Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f" Exception: {e}")
        return False

if __name__ == "__main__":
    test_simple_message()
