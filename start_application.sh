#!/bin/bash
# FreeMobilaChat Startup Script for Linux/macOS
# This script starts the Streamlit application

echo "========================================"
echo "FreeMobilaChat - Starting Application"
echo "========================================"
echo ""

cd streamlit_app || exit 1

echo "Checking Python installation..."
python3 --version || {
    echo "Error: Python 3 is not installed"
    exit 1
}

echo ""
echo "Starting Streamlit application..."
echo "Application will be available at: http://localhost:8501"
echo ""
echo "Press CTRL+C to stop the application"
echo "========================================"
echo ""

streamlit run app.py

