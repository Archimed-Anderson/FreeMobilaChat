"""
Streamlit Cloud deployment entry point
This file is specifically for Streamlit Cloud deployment
"""

import sys
import os

# Add the streamlit_app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()
