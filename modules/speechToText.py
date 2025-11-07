import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        transcript = openai.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f
        )
    return transcript.text.strip()