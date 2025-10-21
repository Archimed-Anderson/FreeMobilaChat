"""
Test Ollama API with httpx (same as LLMAnalyzer)
"""
import httpx
import asyncio
import json

async def test_httpx():
    """Test Ollama with httpx.AsyncClient"""
    print("🔍 Testing Ollama API with httpx...")
    
    # Create client with base_url (same as LLMAnalyzer)
    client = httpx.AsyncClient(
        base_url="http://localhost:11434",
        timeout=60.0
    )
    
    payload = {
        "model": "phi3:mini",
        "messages": [
            {
                "role": "user",
                "content": "Say hello in JSON format: {\"message\": \"hello\"}"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 100
    }
    
    print(f"Base URL: {client.base_url}")
    print(f"Endpoint: /v1/chat/completions")
    print(f"Full URL: {client.base_url}/v1/chat/completions")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = await client.post("/v1/chat/completions", json=payload)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(" httpx works!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f" Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f" Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_httpx())

