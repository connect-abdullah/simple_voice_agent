from faster_whisper import WhisperModel
from config import OPENAI_API_KEY
import os

# Use local cache directory to avoid permission issues
cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
os.makedirs(cache_dir, exist_ok=True)

# Initialize model with local cache
model = None

def get_model():
    """Lazy load the Whisper model to avoid startup delays"""
    global model
    if model is None:
        try:
            model = WhisperModel("small", device="cpu", download_root=cache_dir)
        except Exception as e:
            print(f"⚠️  Failed to load local Whisper model: {e}")
            print("🔄 Falling back to OpenAI Whisper API...")
            model = "openai_fallback"
    return model

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio file using local faster-whisper model or OpenAI API fallback.
    """
    whisper_model = get_model()
    
    if whisper_model == "openai_fallback":
        # Fallback to OpenAI Whisper API
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            with open(file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            print(f"❌ OpenAI Whisper API also failed: {e}")
            return "Transcription failed"
    else:
        # Use local faster-whisper model
        try:
            segments, info = whisper_model.transcribe(file_path)
            text = " ".join(segment.text.strip() for segment in segments)
            return text
        except Exception as e:
            print(f"❌ Local Whisper transcription failed: {e}")
            return "Transcription failed"