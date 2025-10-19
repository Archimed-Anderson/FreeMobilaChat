#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check database directly
"""

import asyncio
import asyncpg
import json
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def check_database():
    """Check database content"""
    
    # Connect to PostgreSQL
    conn = await asyncpg.connect(
        host='localhost',
        port=5433,
        user='postgres',
        password='FreeMobilaChat2024SecurePassword!',
        database='freemobilachat_db'
    )
    
    try:
        # Check conversations
        print("=== CONVERSATIONS ===")
        conversations = await conn.fetch("SELECT id, session_id, title, message_count, status FROM conversations LIMIT 5")
        print(f"Total conversations: {len(conversations)}")
        for conv in conversations:
            print(f"  - ID: {conv['id']}")
            print(f"    Session: {conv['session_id']}")
            print(f"    Title: {conv['title']}")
            print(f"    Messages: {conv['message_count']}")
            print(f"    Status: {conv['status']}")
        
        # Check messages
        print("\n=== MESSAGES ===")
        messages = await conn.fetch("SELECT id, conversation_id, role, content FROM chat_messages LIMIT 5")
        print(f"Total messages: {len(messages)}")
        for msg in messages:
            print(f"  - ID: {msg['id']}")
            print(f"    Conversation: {msg['conversation_id']}")
            print(f"    Role: {msg['role']}")
            print(f"    Content: {msg['content'][:50]}...")
        
        # Check documents
        print("\n=== DOCUMENTS ===")
        documents = await conn.fetch("SELECT id, title, source_url FROM knowledge_documents LIMIT 5")
        print(f"Total documents: {len(documents)}")
        for doc in documents:
            print(f"  - ID: {doc['id']}")
            print(f"    Title: {doc['title']}")
            print(f"    URL: {doc['source_url']}")
        
        # Check feedback
        print("\n=== FEEDBACK ===")
        feedback = await conn.fetch("SELECT id, conversation_id, rating FROM chat_feedback LIMIT 5")
        print(f"Total feedback: {len(feedback)}")
        for fb in feedback:
            print(f"  - ID: {fb['id']}")
            print(f"    Conversation: {fb['conversation_id']}")
            print(f"    Rating: {fb['rating']}")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_database())

