#!/usr/bin/env python3
"""
Test direct de l'Agent Agno avec Ollama
"""
import os
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 80)
print("TEST DIRECT AGNO + OLLAMA")
print("=" * 80)

# Test 1: Import des modules
print("\n1. Test des imports...")
try:
    from agno.models.ollama import Ollama
    from agno.agent import Agent
    print("✅ Imports réussis")
except Exception as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

# Test 2: Création du modèle Ollama
print("\n2. Création du modèle Ollama...")
try:
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    print(f"   URL Ollama: {ollama_url}")
    
    model = Ollama(id="mistral:latest", host=ollama_url)
    print("✅ Modèle Ollama créé")
except Exception as e:
    print(f"❌ Erreur création modèle: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Création de l'Agent
print("\n3. Création de l'Agent Agno...")
try:
    agent = Agent(
        name="Test Agent",
        model=model,
        markdown=True,
        description="Agent de test"
    )
    print("✅ Agent Agno créé")
except Exception as e:
    print(f"❌ Erreur création agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Génération d'une réponse simple
print("\n4. Test de génération de réponse...")
try:
    print("   Envoi du message: 'Bonjour, comment vas-tu ?'")
    response = agent.run("Bonjour, comment vas-tu ?")
    
    # Extraire le contenu de la réponse
    if hasattr(response, 'content'):
        response_text = response.content
    elif isinstance(response, str):
        response_text = response
    else:
        response_text = str(response)
    
    print(f"✅ Réponse reçue ({len(response_text)} caractères):")
    print(f"   {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
except Exception as e:
    print(f"❌ Erreur génération réponse: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Génération d'une réponse technique
print("\n5. Test de génération de réponse technique...")
try:
    print("   Envoi du message: 'Comment activer la 4G sur Free Mobile ?'")
    response = agent.run("Comment activer la 4G sur Free Mobile ?")
    
    # Extraire le contenu de la réponse
    if hasattr(response, 'content'):
        response_text = response.content
    elif isinstance(response, str):
        response_text = response
    else:
        response_text = str(response)
    
    print(f"✅ Réponse reçue ({len(response_text)} caractères):")
    print(f"   {response_text[:300]}{'...' if len(response_text) > 300 else ''}")
except Exception as e:
    print(f"❌ Erreur génération réponse: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ TOUS LES TESTS SONT PASSÉS")
print("=" * 80)

