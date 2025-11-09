#!/bin/bash

# FreeMobilaChat Full Application Startup Script for Linux/Mac
# This script starts BOTH the FastAPI backend AND the Streamlit frontend

echo "========================================"
echo "FreeMobilaChat - Full Application Start"
echo "========================================"
echo ""
echo "This will start:"
echo "  1. FastAPI Backend (port 8000)"
echo "  2. Streamlit Frontend (port 8501)"
echo ""
echo "========================================"
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi
python3 --version
echo "Python OK!"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "Virtual environment activated!"
else
    echo "Warning: No virtual environment found"
    echo "Continuing with system Python..."
fi
echo ""

# Start Backend in background
echo "Starting FastAPI Backend on http://localhost:8000..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

echo ""
echo "Starting Streamlit Frontend on http://localhost:8501..."
cd streamlit_app
python3 -m streamlit run app.py --server.port 8501

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null

