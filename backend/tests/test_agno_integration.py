#!/usr/bin/env python3
"""
Test d'intégration de l'Agent Agno
"""
import requests
import sys
import json

def test_agno_integration():
    """Test de l'intégration de l'Agent Agno via l'API HTTP"""
    print("=" * 80)
    print("TEST D'INTÉGRATION DE L'AGENT AGNO")
    print("=" * 80)

    # URL de l'API
    api_url = "http://localhost:8000/api/chatbot/message"

    # Créer un message de test
    print("\n1⃣ Envoi d'un message de test à l'API...")
    test_data = {
        "message": "Bonjour, comment puis-je activer la 4G sur mon téléphone Free Mobile ?",
        "session_id": "test_agno_integration",
        "llm_provider": "ollama"
    }

    print(f"   Message: {test_data['message']}")
    print(f"   Provider: {test_data['llm_provider']}")

    # Envoyer le message
    try:
        response = requests.post(api_url, json=test_data, timeout=60)

        if response.status_code != 200:
            print(f"\n ÉCHEC : Code HTTP {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False

        result = response.json()

        print("\n2⃣ Réponse reçue:")
        print(f"   Success: {result.get('success')}")
        print(f"   Conversation ID: {result.get('conversation_id')}")
        print(f"   Message ID: {result.get('message_id')}")
        print(f"   LLM Provider: {result.get('llm_provider')}")
        print(f"   Processing Time: {result.get('processing_time')}s")

        response_text = result.get('response', '')
        print(f"\n3⃣ Réponse (premiers 300 caractères):")
        print(f"   {response_text[:300]}...")

        # Vérifier que la réponse n'est pas une réponse simulée
        if "Je suis en cours de développement" in response_text:
            print("\n ÉCHEC : La réponse est une réponse simulée")
            print(" L'Agent Agno n'a pas généré de réponse")
            return False

        print("\n SUCCÈS : L'Agent Agno a généré une réponse")
        return True

    except requests.exceptions.Timeout:
        print("\n ERREUR : Timeout lors de la requête (>60s)")
        return False
    except Exception as e:
        print(f"\n ERREUR lors du traitement du message: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    success = test_agno_integration()

    print("\n" + "=" * 80)
    if success:
        print(" TEST D'INTÉGRATION AGNO : SUCCÈS")
        print("=" * 80)
        sys.exit(0)
    else:
        print(" TEST D'INTÉGRATION AGNO : ÉCHEC")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()

