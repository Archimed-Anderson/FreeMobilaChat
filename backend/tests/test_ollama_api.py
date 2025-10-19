import httpx
import asyncio
import json

async def test_ollama():
    """Test Ollama API with httpx"""
    client = httpx.AsyncClient(
        base_url='http://localhost:11434',
        timeout=60.0
    )
    
    payload = {
        'model': 'phi3:mini',
        'messages': [
            {'role': 'system', 'content': 'Tu es un expert en analyse de satisfaction client pour Free (opérateur télécom français). Tu analyses les tweets du service client avec précision. Réponds UNIQUEMENT en JSON valide, sans markdown ni commentaires.'},
            {'role': 'user', 'content': '''Analyse ce tweet et retourne un JSON avec les champs suivants:
- sentiment: "positive", "negative" ou "neutral"
- sentiment_score: score entre 0 et 1
- category: "technical", "commercial", "customer_service", "billing", "network" ou "other"
- priority: "critical", "high", "medium" ou "low"
- keywords: liste de 3-5 mots-clés
- is_urgent: true ou false
- needs_response: true ou false

Tweet: "Service client excellent! Merci Free Mobile."'''}
        ],
        'temperature': 0.2,
        'max_tokens': 400
    }
    
    try:
        print("Envoi de la requête à Ollama...")
        response = await client.post('/v1/chat/completions', json=payload)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nRéponse complète:")
            print(json.dumps(data, indent=2))
            
            content = data['choices'][0]['message']['content'].strip()
            print("\nContenu du message:")
            print(content)
            
            # Try to parse as JSON
            content = content.replace("```json", "").replace("```", "").strip()
            try:
                parsed = json.loads(content)
                print("\nJSON parsé avec succès:")
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError as e:
                print(f"\nErreur de parsing JSON: {e}")
        else:
            print(f"Erreur: {response.text}")
    
    except Exception as e:
        print(f"Exception: {e}")
    
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_ollama())

