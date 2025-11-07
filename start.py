#!/usr/bin/env python3
"""
Simple startup script for Voice Agent
Starts both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import os

def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_process = subprocess.Popen([
        sys.executable, "backend/main.py"
    ], cwd=os.path.dirname(os.path.abspath(__file__)))
    return backend_process

def start_frontend():
    """Start Streamlit frontend"""
    print("🌐 Starting Streamlit frontend...")
    frontend_process = subprocess.Popen([
        "streamlit", "run", "frontend/app.py"
    ], cwd=os.path.dirname(os.path.abspath(__file__)))
    return frontend_process

def main():
    print("🎤 Voice Agent Startup")
    print("=" * 30)
    
    # Start backend
    backend = start_backend()
    time.sleep(2)  # Give backend time to start
    
    # Start frontend
    frontend = start_frontend()
    
    print("\n✅ Services started!")
    print("📡 Backend API: http://localhost:8000")
    print("🌐 Frontend UI: http://localhost:8501")
    print("\nPress Ctrl+C to stop both services")
    
    try:
        # Wait for processes
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend.terminate()
        frontend.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()
