"""
Test Ollama analysis with detailed logging
"""
import requests
import json

# Test endpoint
url = "http://localhost:8000/test-analyze-single"

# Test data
payload = {
    "text": "Merci Free pour votre excellent service! Très satisfait.",
    "provider": "ollama"
}

print("=" * 80)
print("🔍 TESTING OLLAMA ANALYSIS WITH DETAILED LOGGING")
print("=" * 80)
print(f"\n📤 Sending request to: {url}")
print(f"📋 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
print("\n" + "=" * 80)

try:
    response = requests.post(url, json=payload, timeout=120)
    print(f"\n📥 Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n SUCCESS!")
        print(f"\n Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🔍 Check backend/logs/app.log for detailed Ollama API logs")
print("=" * 80)

