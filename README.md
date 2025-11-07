# Voice Agent

A simple voice agent application with Streamlit frontend and FastAPI backend.

## Features

- 🎤 Voice recording and transcription
- 🤖 AI chat responses using OpenAI
- 🔊 Text-to-speech using ElevenLabs
- 🎵 Voice selection (Rachel, Domi, Bella)
- 💬 Text input option

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   ```

3. **Install ffmpeg (required for audio playback):**
   ```bash
   brew install ffmpeg  # macOS
   ```

## Running the Application

### Start the Backend (Terminal 1):
```bash
cd backend
python main.py
```
The API will be available at `http://localhost:8000`

### Start the Frontend (Terminal 2):
```bash
cd frontend
streamlit run app.py
```
The web interface will open at `http://localhost:8501`

## API Endpoints

- `GET /` - Health check
- `GET /voices` - Get available voices
- `POST /transcribe` - Transcribe audio to text
- `POST /chat` - Get AI response from text
- `POST /tts` - Convert text to speech

## Usage

1. Select a voice from the dropdown
2. Either:
   - Record your voice using the microphone button
   - Type your message in the text area
3. The AI will respond with text and speech

## File Structure

```
voice_agent/
├── backend/
│   └── main.py          # FastAPI backend
├── frontend/
│   └── app.py           # Streamlit frontend
├── modules/
│   ├── llm.py           # OpenAI integration
│   ├── speechToText.py  # Speech transcription
│   └── textToSpeech.py  # Text-to-speech
├── config.py            # Configuration
├── requirements.txt     # Dependencies
└── README.md           # This file
```
