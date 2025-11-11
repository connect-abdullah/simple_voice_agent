from config import OPENAI_API_KEY
from openai import OpenAI
import os
import time

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.
    """
    try:
        start_time = time.time()
        file_size = os.path.getsize(file_path)
        print(f"🎤 Starting transcription: {file_path} ({file_size} bytes)")
        
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        elapsed = time.time() - start_time
        print(f"✅ Transcription completed in {elapsed:.2f}s")
        
        return transcript if isinstance(transcript, str) else transcript.text
    except Exception as e:
        print(f"❌ Whisper API transcription failed: {e}")
        import traceback
        traceback.print_exc()
        return "Transcription failed"