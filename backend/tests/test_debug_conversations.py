#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check conversations endpoint
"""

import requests
import json
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000"

# Test 1: Get conversations for test_user
print("Test 1: GET /api/chatbot/conversations/test_user")
response = requests.get(f"{BASE_URL}/api/chatbot/conversations/test_user")
print(f"Status: {response.status_code}")
print(f"Response type: {type(response.json())}")
print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

# Test 2: Get conversations for session_id
print("\n\nTest 2: GET /api/chatbot/conversations?session_id=test_session_1760775343")
response = requests.get(f"{BASE_URL}/api/chatbot/conversations?session_id=test_session_1760775343")
print(f"Status: {response.status_code}")
print(f"Response type: {type(response.json())}")
print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")

