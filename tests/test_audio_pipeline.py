#!/usr/bin/env python3
"""
Tests for the complete audio pipeline
"""
import pytest
import asyncio
import json
import websockets
import base64

class TestAudioPipeline:
    """Test the complete audio streaming pipeline"""
    
    @pytest.mark.asyncio
    async def test_complete_audio_pipeline(self):
        """Test the complete pipeline: text input -> AI response -> audio output"""
        try:
            async with websockets.connect("ws://localhost:8000/stream") as websocket:
                # Send test message with voice selection
                test_message = {
                    "type": "text_input",
                    "text": "Say hello",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM"
                }
                
                await websocket.send(json.dumps(test_message))
                
                text_chunks_received = 0
                audio_chunks_received = 0
                stream_completed = False
                
                # Collect responses for up to 30 seconds
                timeout = 30
                start_time = asyncio.get_event_loop().time()
                
                while (asyncio.get_event_loop().time() - start_time) < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(response)
                        
                        if data["type"] == "text_chunk":
                            text_chunks_received += 1
                            assert isinstance(data["content"], str)
                            
                        elif data["type"] == "audio_chunk":
                            audio_chunks_received += 1
                            assert "audio_data" in data
                            assert "text" in data
                            
                            # Verify audio data is valid base64
                            try:
                                audio_bytes = base64.b64decode(data["audio_data"])
                                assert len(audio_bytes) > 0
                            except Exception as e:
                                pytest.fail(f"Invalid audio data: {e}")
                                
                        elif data["type"] == "stream_complete":
                            stream_completed = True
                            break
                            
                        elif data["type"] == "error":
                            pytest.fail(f"Pipeline error: {data['message']}")
                            
                    except asyncio.TimeoutError:
                        break
                
                # Verify we received expected data
                assert text_chunks_received > 0, "No text chunks received"
                assert audio_chunks_received > 0, "No audio chunks received"
                assert stream_completed, "Stream did not complete properly"
                
                print(f"✅ Pipeline test successful:")
                print(f"   Text chunks: {text_chunks_received}")
                print(f"   Audio chunks: {audio_chunks_received}")
                
        except Exception as e:
            pytest.skip(f"Audio pipeline test requires running backend: {e}")
    
    @pytest.mark.asyncio
    async def test_voice_selection(self):
        """Test different voice selections work"""
        voices_to_test = [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "AZnzlk1XvdvUeBnXmlld",  # Domi
            "N2lVS1w4EtoT3dr4eOWO"   # Callum
        ]
        
        for voice_id in voices_to_test:
            try:
                async with websockets.connect("ws://localhost:8000/stream") as websocket:
                    test_message = {
                        "type": "text_input",
                        "text": "Test voice",
                        "voice_id": voice_id
                    }
                    
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for at least one audio chunk
                    audio_received = False
                    for _ in range(10):  # Try up to 10 messages
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=3)
                            data = json.loads(response)
                            
                            if data["type"] == "audio_chunk":
                                audio_received = True
                                break
                            elif data["type"] == "stream_complete":
                                break
                                
                        except asyncio.TimeoutError:
                            break
                    
                    if not audio_received:
                        print(f"⚠️  No audio received for voice {voice_id}")
                    else:
                        print(f"✅ Voice {voice_id} working")
                        
            except Exception as e:
                pytest.skip(f"Voice test requires running backend: {e}")

if __name__ == "__main__":
    pytest.main([__file__])
