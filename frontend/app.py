import streamlit as st
import requests
import tempfile
import os
from audio_recorder_streamlit import audio_recorder
import base64
import io

# Configuration
API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Voice Agent",
    page_icon="🎤",
    layout="centered"
)

def get_voices():
    """Get available voices from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/voices")
        if response.status_code == 200:
            return response.json()["voices"]
        else:
            st.error("Failed to fetch voices")
            return {}
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the backend is running on port 8000.")
        return {}

def transcribe_audio(audio_bytes):
    """Send audio to API for transcription"""
    try:
        files = {"audio": ("audio.wav", audio_bytes, "audio/wav")}
        response = requests.post(f"{API_BASE_URL}/transcribe", files=files)
        if response.status_code == 200:
            return response.json()["text"]
        else:
            st.error(f"Transcription failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the backend is running.")
        return None

def get_ai_response(text):
    """Get AI response from text"""
    try:
        data = {"text": text}
        response = requests.post(f"{API_BASE_URL}/chat", json=data)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            st.error(f"AI response failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the backend is running.")
        return None

def get_speech_audio(text, voice_id):
    """Get speech audio from text"""
    try:
        data = {"text": text, "voice_id": voice_id}
        response = requests.post(f"{API_BASE_URL}/tts", json=data)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Text-to-speech failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the backend is running.")
        return None

def main():
    st.title("🎤 Voice Agent")
    st.markdown("---")
    
    # Voice selection
    voices = get_voices()
    if not voices:
        st.stop()
    
    st.subheader("🎵 Select Voice")
    voice_options = {f"{info['name']} - {info['description']}": info['id'] 
                    for info in voices.values()}
    
    selected_voice_display = st.selectbox(
        "Choose a voice:",
        options=list(voice_options.keys()),
        index=0
    )
    selected_voice_id = voice_options[selected_voice_display]
    
    st.markdown("---")
    
    # Audio recording section
    st.subheader("🎙️ Speak to the AI")
    st.write("Click the microphone to start recording, click again to stop.")
    
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e74c3c",
        neutral_color="#34495e",
        icon_name="microphone",
        icon_size="2x"
    )
    
    if audio_bytes:
        st.success("Audio recorded successfully!")
        
        # Transcribe audio
        with st.spinner("Transcribing audio..."):
            transcribed_text = transcribe_audio(audio_bytes)
        
        if transcribed_text:
            st.subheader("📝 Your Message")
            st.write(f"**You said:** {transcribed_text}")
            
            # Get AI response
            with st.spinner("Getting AI response..."):
                ai_response = get_ai_response(transcribed_text)
            
            if ai_response:
                st.subheader("🤖 AI Response")
                st.write(f"**AI:** {ai_response}")
                
                # Generate and auto-play speech
                with st.spinner("Generating speech..."):
                    speech_audio = get_speech_audio(ai_response, selected_voice_id)
                
                if speech_audio:
                    # Auto-play the audio response
                    st.audio(speech_audio, format="audio/mp3", autoplay=True)

if __name__ == "__main__":
    main()
