"""
Test Ollama API directly
"""
import requests
import json

# Test Ollama API
print("🔍 Testing Ollama API...")

url = "http://localhost:11434/v1/chat/completions"
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

print(f"Sending request to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Ollama API works!")
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

