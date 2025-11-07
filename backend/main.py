from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.speechToText import transcribe_audio
from modules.llm import generate_reply
from modules.textToSpeech import speak_text
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

class TTSRequest(BaseModel):
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

@app.post("/chat")
async def chat_endpoint(request: TextRequest):
    """Generate AI response from text"""
    try:
        reply = generate_reply(request.text)
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/tts")
async def text_to_speech_endpoint(request: TTSRequest):
    """Convert text to speech and return audio file"""
    try:
        # Convert voice_id (name or ID) to actual voice ID
        voice_id = get_voice_id(request.voice_id) if request.voice_id else DEFAULT_VOICE_ID
        
        # Generate audio file
        from modules.textToSpeech import generate_speech_audio
        audio_path = generate_speech_audio(request.text, voice_id)
        
        # Read audio file
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up
        os.unlink(audio_path)
        
        from fastapi.responses import Response
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
