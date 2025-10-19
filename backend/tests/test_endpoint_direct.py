"""
Test endpoint directly with detailed debugging
"""
import requests
import json
import time

print("=" * 80)
print("🔍 TESTING /test-analyze-single ENDPOINT")
print("=" * 80)

# Test 1: Check if server is running
print("\n📡 Test 1: Checking if server is running...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"✅ Server is running: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"❌ Server is not running: {e}")
    exit(1)

# Test 2: List all available endpoints
print("\n📋 Test 2: Listing available endpoints...")
try:
    response = requests.get("http://localhost:8000/openapi.json", timeout=5)
    if response.status_code == 200:
        openapi = response.json()
        paths = openapi.get("paths", {})
        print(f"✅ Found {len(paths)} endpoints:")
        for path in sorted(paths.keys()):
            methods = list(paths[path].keys())
            print(f"   - {path}: {methods}")
            
        # Check if /test-analyze-single exists
        if "/test-analyze-single" in paths:
            print(f"\n✅ /test-analyze-single endpoint EXISTS")
            print(f"   Methods: {list(paths['/test-analyze-single'].keys())}")
        else:
            print(f"\n❌ /test-analyze-single endpoint NOT FOUND")
    else:
        print(f"❌ Failed to get OpenAPI spec: {response.status_code}")
except Exception as e:
    print(f"❌ Error getting OpenAPI spec: {e}")

# Test 3: Call /test-analyze-single with GET (should fail)
print("\n🧪 Test 3: Calling /test-analyze-single with GET (should fail)...")
try:
    response = requests.get("http://localhost:8000/test-analyze-single", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Call /test-analyze-single with POST (correct method)
print("\n🧪 Test 4: Calling /test-analyze-single with POST...")
try:
    payload = {
        "text": "Merci Free pour votre excellent service!",
        "provider": "ollama"
    }
    print(f"   Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    response = requests.post(
        "http://localhost:8000/test-analyze-single",
        json=payload,
        timeout=120
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Wait and check logs
print("\n📝 Test 5: Checking logs...")
print("   Waiting 2 seconds for logs to be written...")
time.sleep(2)

try:
    with open("backend/logs/app.log", "r", encoding="utf-8") as f:
        lines = f.readlines()
        print(f"   Total log lines: {len(lines)}")
        print(f"   Last 10 lines:")
        for line in lines[-10:]:
            print(f"      {line.rstrip()}")
except Exception as e:
    print(f"   Error reading logs: {e}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)

