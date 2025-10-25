"""
Vercel serverless function entry point
This file is specifically for Vercel deployment
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the FastAPI app
from app.main import app

# Export the app for Vercel
handler = app
