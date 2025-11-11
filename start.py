#!/usr/bin/env python3
"""
Voice Agent Startup Script
Starts both FastAPI backend and Web frontend for voice conversations
"""

import subprocess
import sys
import time
import os
import signal
import threading
from pathlib import Path

def start_backend():
    """Start FastAPI backend with streaming WebSocket support"""
    print("🚀 Starting FastAPI backend...")
    backend_process = subprocess.Popen([
        sys.executable, "backend/main.py"
    ], cwd=os.path.dirname(os.path.abspath(__file__)),
    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    return backend_process

def start_frontend():
    """Start Next.js frontend with voice interface"""
    print("🌐 Starting Next.js frontend...")
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nextjs-frontend")
    
    # Check if Next.js frontend exists
    if not os.path.exists(frontend_dir):
        print("⚠️  Next.js frontend not found, falling back to simple frontend...")
        frontend_process = subprocess.Popen([
            sys.executable, "web-frontend/server.py"
        ], cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        return frontend_process
    
    # Start Next.js dev server
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=frontend_dir,
    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    return frontend_process

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import websockets
        import openai
        import elevenlabs
        import faster_whisper
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if required environment variables are set"""
    from config import OPENAI_API_KEY, ELEVENLABS_API_KEY
    
    issues = []
    if not OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY")
    if not ELEVENLABS_API_KEY:
        issues.append("ELEVENLABS_API_KEY")
    
    if issues:
        print(f"❌ Missing environment variables: {', '.join(issues)}")
        print("💡 Create a .env file with your API keys")
        return False
    
    print("✅ Environment variables configured")
    return True

def cleanup_port(port):
    """Kill any process using the specified port"""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    pid_int = int(pid.strip())
                    # Try graceful termination first
                    try:
                        os.kill(pid_int, signal.SIGTERM)
                        time.sleep(0.5)  # Give process time to terminate
                        # Check if process still exists and force kill if needed
                        os.kill(pid_int, 0)  # This will raise ProcessLookupError if process is gone
                        os.kill(pid_int, signal.SIGKILL)  # Force kill if still running
                        time.sleep(0.2)
                    except ProcessLookupError:
                        pass  # Process already terminated, which is fine
                    print(f"🔧 Freed port {port} (killed process {pid_int})")
                except (ValueError, ProcessLookupError, PermissionError):
                    pass
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return False

def cleanup_ports():
    """Clean up ports 8000 and 3000 before starting services"""
    print("🧹 Checking for processes using required ports...")
    backend_port_freed = cleanup_port(8000)
    frontend_port_freed = cleanup_port(3000)
    
    if backend_port_freed or frontend_port_freed:
        time.sleep(1)  # Give ports time to be released
        print("✅ Ports are ready")
    else:
        print("✅ Ports are available")

def wait_for_backend(backend_process, max_attempts=30):
    """Wait for backend to be ready"""
    import requests
    
    for attempt in range(max_attempts):
        # Check if process is still running
        if backend_process.poll() is not None:
            # Process has terminated, get the error output
            try:
                _, stderr = backend_process.communicate(timeout=1)
                print(f"\n❌ Backend process terminated unexpectedly!")
                if stderr:
                    print(f"Error output: {stderr}")
            except subprocess.TimeoutExpired:
                print(f"\n❌ Backend process terminated unexpectedly!")
            return False
        
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt == 0:
            print("⏳ Waiting for backend to start...", end="", flush=True)
        elif attempt % 10 == 0:
            print(f"\n⏳ Still waiting... ({attempt}/{max_attempts})", end="", flush=True)
        else:
            print(".", end="", flush=True)
        
        time.sleep(1)
    
    print(f"\n❌ Backend failed to start within {max_attempts} seconds")
    return False

def main():
    """Main startup function"""
    print("🎤 Streaming Voice Agent Startup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Clean up ports before starting
    print("\n🧹 Preparing ports...")
    cleanup_ports()
    
    # Start backend
    print("\n🔧 Starting services...")
    backend = start_backend()
    
    # Wait for backend to be ready
    if not wait_for_backend(backend):
        backend.terminate()
        sys.exit(1)
    
    # Start frontend
    frontend = start_frontend()
    time.sleep(3)  # Give frontend time to start
    
    print("\n🎉 Voice Agent is ready!")
    print("=" * 40)
    print("📡 Backend API: http://localhost:8000")
    print("🌐 Frontend UI: http://localhost:3000")
    print("🔌 WebSocket: ws://localhost:8000/stream")
    print("\n🎯 Features:")
    print("  • Voice-only interface")
    print("  • Real-time AI streaming responses")
    print("  • ElevenLabs voice selection")
    print("  • Whisper speech recognition")
    print("  • Sequential audio playback")
    print("\n⌨️  Commands:")
    print("  • Press Ctrl+C to stop all services")
    print("  • Open http://localhost:3000 in your browser")
    print("  • Run tests with: python -m pytest tests/")
    
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down services...")
        backend.terminate()
        frontend.terminate()
        
        # Wait for processes to terminate
        try:
            backend.wait(timeout=5)
            frontend.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend.kill()
            frontend.kill()
        
        print("✅ All services stopped")
        sys.exit(0)
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Keep the script running and monitor processes
        while True:
            # Check if processes are still running
            backend_status = backend.poll()
            frontend_status = frontend.poll()
            
            if backend_status is not None:
                print("\n❌ Backend process died unexpectedly")
                try:
                    _, stderr = backend.communicate(timeout=1)
                    if stderr:
                        print(f"Backend error: {stderr}")
                except subprocess.TimeoutExpired:
                    pass
                frontend.terminate()
                sys.exit(1)
            
            if frontend_status is not None:
                print("\n❌ Frontend process died unexpectedly")
                try:
                    _, stderr = frontend.communicate(timeout=1)
                    if stderr:
                        print(f"Frontend error: {stderr}")
                except subprocess.TimeoutExpired:
                    pass
                backend.terminate()
                sys.exit(1)
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
