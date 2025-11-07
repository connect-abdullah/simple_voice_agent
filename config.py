import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Free plan voices available: "Rachel", "Domi", "Bella"
FREE_VOICES = {
    "1": {
        "id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
        "name": "Rachel",
        "description": "Calm and professional female voice"
    },
    "2": {
        "id": "AZnzlk1XvdvUeBnXmlld",  # Domi
        "name": "Domi",
        "description": "Strong and confident female voice"
    },
    "3": {
        "id": "N2lVS1w4EtoT3dr4eOWO",  # Bella
        "name": "Callum",
        "description": "Deceptively gravelly, yet unsettling edge."
    }
}

DEFAULT_VOICE = "Rachel"  # Default fallback voice name
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel's voice ID
SAMPLE_RATE = 16000

def get_voice_id_by_name(name):
    """Get voice ID by voice name"""
    for voice_info in FREE_VOICES.values():
        if voice_info["name"] == name:
            return voice_info["id"]
    return DEFAULT_VOICE_ID  # Fallback to Rachel

def get_voice_id(voice_identifier):
    """Get voice ID from either a name or ID"""
    # Check if it's already an ID (check if it exists in any voice)
    for voice_info in FREE_VOICES.values():
        if voice_info["id"] == voice_identifier:
            return voice_identifier
        if voice_info["name"] == voice_identifier:
            return voice_info["id"]
    # If not found, return default
    return DEFAULT_VOICE_ID
