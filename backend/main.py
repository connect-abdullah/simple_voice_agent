from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
import sys
import asyncio
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.speechToText import transcribe_audio
from modules.llm import gpt_stream_to_queue
from modules.simple_tts import simple_elevenlabs_streamer, openai_tts_streamer, simple_elevenlabs_streamer_websocket, openai_tts_streamer_websocket
from config import FREE_VOICES, DEFAULT_VOICE_ID, get_voice_id

app = FastAPI(title="Voice Agent API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None  # Will default to DEFAULT_VOICE_ID

@app.get("/")
async def root():
    return {"message": "Voice Agent API is running"}

@app.get("/voices")
async def get_voices():
    """Get available voices"""
    return {"voices": FREE_VOICES}

@app.post("/transcribe")
async def transcribe_audio_endpoint(audio: UploadFile = File(...)):
    """Transcribe audio file to text"""
    if not audio.filename.endswith(('.wav', '.mp3', '.m4a', '.webm')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as tmp_file:
        content = await audio.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Transcribe audio
        text = transcribe_audio(tmp_path)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming voice conversation"""
    await websocket.accept()
    
    try:
        while True:
            # Wait for text input from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "text_input":
                user_text = message["text"]
                voice_id = message.get("voice_id", DEFAULT_VOICE_ID)  # Use selected voice or default
                
                # Create separate queues for TTS and WebSocket
                tts_queue = asyncio.Queue()
                websocket_queue = asyncio.Queue()
                
                # Create a modified streaming function that sends to both queues
                async def gpt_stream_with_dual_output(user_input: str, tts_queue: asyncio.Queue, ws_queue: asyncio.Queue):
                    """Stream GPT response to both TTS queue and WebSocket queue"""
                    import concurrent.futures
                    from openai import OpenAI
                    from config import OPENAI_API_KEY
                    
                    client = OpenAI(api_key=OPENAI_API_KEY)
                    
                    def create_stream():
                        return client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": user_input}],
                            stream=True
                        )
                    
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        stream = await loop.run_in_executor(executor, create_stream)
                        
                        def get_next_chunk():
                            try:
                                return next(stream)
                            except StopIteration:
                                return None
                        
                        while True:
                            chunk = await loop.run_in_executor(executor, get_next_chunk)
                            if chunk is None:
                                break
                                
                            if chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content
                                print(content, end="", flush=True)
                                # Send to both queues independently
                                await tts_queue.put(content)
                                await ws_queue.put(content)
                    
                    # Signal end to both queues
                    await tts_queue.put(None)
                    await ws_queue.put(None)
                
                # Start streaming tasks
                gpt_task = asyncio.create_task(gpt_stream_with_dual_output(user_text, tts_queue, websocket_queue))
                
                # Start TTS task that sends audio to WebSocket
                async def tts_with_websocket(tts_queue, websocket, voice_id):
                    """Generate TTS and send audio chunks via WebSocket"""
                    # Try ElevenLabs first with selected voice, fallback to OpenAI TTS
                    try:
                        print(f"🔊 Starting ElevenLabs TTS with voice: {voice_id}...")
                        await simple_elevenlabs_streamer_websocket(tts_queue, websocket, voice_id)
                        print("✅ ElevenLabs TTS completed")
                    except Exception as e:
                        print(f"⚠️  ElevenLabs failed, using OpenAI TTS: {e}")
                        try:
                            print("🔊 Starting OpenAI TTS...")
                            await openai_tts_streamer_websocket(tts_queue, websocket)
                            print("✅ OpenAI TTS completed")
                        except Exception as e2:
                            print(f"❌ OpenAI TTS also failed: {e2}")
                            import traceback
                            traceback.print_exc()
                
                tts_task = asyncio.create_task(tts_with_websocket(tts_queue, websocket, voice_id))
                
                # Stream text chunks to WebSocket
                async def stream_to_websocket():
                    while True:
                        chunk = await websocket_queue.get()
                        if chunk is None:
                            break
                        await websocket.send_text(json.dumps({
                            "type": "text_chunk",
                            "content": chunk
                        }))
                
                websocket_task = asyncio.create_task(stream_to_websocket())
                
                # Wait for all tasks to complete
                await asyncio.gather(gpt_task, tts_task, websocket_task)
                
                # Send completion signal to client
                await websocket.send_text(json.dumps({"type": "stream_complete"}))
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
