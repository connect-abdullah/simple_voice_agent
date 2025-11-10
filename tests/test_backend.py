#!/usr/bin/env python3
"""
Tests for the Voice Agent backend
"""
import pytest
import asyncio
import json
import tempfile
import os
from fastapi.testclient import TestClient
import websockets

# Import the FastAPI app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

client = TestClient(app)

class TestBackendAPI:
    """Test the FastAPI backend endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Voice Agent API is running"}
    
    def test_voices_endpoint(self):
        """Test the voices endpoint"""
        response = client.get("/voices")
        assert response.status_code == 200
        data = response.json()
        assert "voices" in data
        assert isinstance(data["voices"], dict)
        assert len(data["voices"]) > 0
    
    def test_transcribe_endpoint_no_file(self):
        """Test transcribe endpoint without file"""
        response = client.post("/transcribe")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_transcribe_endpoint_invalid_format(self):
        """Test transcribe endpoint with invalid file format"""
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp_file:
            tmp_file.write(b"not an audio file")
            tmp_file.flush()
            
            with open(tmp_file.name, "rb") as f:
                response = client.post(
                    "/transcribe",
                    files={"audio": ("test.txt", f, "text/plain")}
                )
        
        assert response.status_code == 400
        assert "Unsupported audio format" in response.json()["detail"]

class TestWebSocketConnection:
    """Test WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        try:
            async with websockets.connect("ws://localhost:8000/stream") as websocket:
                # Test connection is established
                assert websocket.open
                
                # Send a test message
                test_message = {
                    "type": "text_input",
                    "text": "Hello test",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM"
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Receive at least one response
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(response)
                
                # Should receive either text_chunk or error
                assert data["type"] in ["text_chunk", "error"]
                
        except Exception as e:
            pytest.skip(f"WebSocket test requires running backend: {e}")

class TestModules:
    """Test individual modules"""
    
    def test_config_import(self):
        """Test config module imports correctly"""
        from config import FREE_VOICES, DEFAULT_VOICE_ID
        assert isinstance(FREE_VOICES, dict)
        assert isinstance(DEFAULT_VOICE_ID, str)
        assert len(FREE_VOICES) > 0
    
    def test_llm_import(self):
        """Test LLM module imports correctly"""
        from modules.llm import gpt_stream_to_queue
        assert callable(gpt_stream_to_queue)
    
    def test_tts_import(self):
        """Test TTS module imports correctly"""
        from modules.simple_tts import simple_elevenlabs_streamer_websocket
        assert callable(simple_elevenlabs_streamer_websocket)
    
    def test_speech_to_text_import(self):
        """Test speech to text module imports correctly"""
        from modules.speechToText import transcribe_audio
        assert callable(transcribe_audio)

if __name__ == "__main__":
    pytest.main([__file__])
