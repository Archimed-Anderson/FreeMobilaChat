#!/usr/bin/env python3
"""
Start the FastAPI backend server
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

if __name__ == "__main__":
    print(" Starting Tweet Analysis Platform Backend Server")
    print("📡 Server will be available at: http://127.0.0.1:8000")
    print("📖 API Documentation: http://127.0.0.1:8000/docs")
    print("🔄 Auto-reload enabled for development")
    print("-" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
