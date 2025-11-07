from elevenlabs.client import ElevenLabs
from elevenlabs import play
from config import ELEVENLABS_API_KEY, DEFAULT_VOICE_ID, get_voice_id
import tempfile
import os

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def speak_text(text, voice_id=None):
    """
    Convert text to speech and play it.
    
    Args:
        text: The text to convert to speech
        voice_id: The voice ID or name to use (defaults to DEFAULT_VOICE_ID from config)
    """
    if voice_id is None:
        voice_id = DEFAULT_VOICE_ID
    else:
        # Convert name to ID if needed
        voice_id = get_voice_id(voice_id)
    
    print("🔊 Speaking...")

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )

    play.play(audio)

def generate_speech_audio(text, voice_id=None):
    """
    Convert text to speech and save as audio file.
    
    Args:
        text: The text to convert to speech
        voice_id: The voice ID or name to use (defaults to DEFAULT_VOICE_ID from config)
    
    Returns:
        str: Path to the generated audio file
    """
    if voice_id is None:
        voice_id = DEFAULT_VOICE_ID
    else:
        # Convert name to ID if needed
        voice_id = get_voice_id(voice_id)
    
    # Get audio stream
    audio_stream = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )
    
    # Collect audio chunks
    audio_bytes = b""
    for chunk in audio_stream:
        if chunk:
            audio_bytes += chunk
    
    # Save to temporary file
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file.write(audio_bytes)
    tmp_file.close()
    
    return tmp_file.name
