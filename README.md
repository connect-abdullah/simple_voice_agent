# 🎤 Voice Agent

A pure voice-to-voice AI agent with real-time streaming responses and voice selection.

## ✨ Features

- 🎤 **Voice-only interface** - Pure speech interaction
- 🤖 **Real-time streaming** AI responses using OpenAI GPT-4
- 🔊 **Sequential audio playback** - No overlapping voices
- 🎵 **Voice selection** - Choose from 3 ElevenLabs voices
- 🎯 **Whisper transcription** - Local + OpenAI API fallback
- ⚡ **Instant responses** - AI speaks as it thinks

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

3. **Install system dependencies:**
   ```bash
   # macOS
   brew install portaudio ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install portaudio19-dev ffmpeg
   ```

## 🚀 Quick Start

**One-command startup:**
```bash
python start.py
```

This will:
- ✅ Check dependencies and environment
- 🚀 Start the FastAPI backend (port 8000)
- 🌐 Start the web frontend (port 3000)
- 🎯 Display service URLs
- 🔄 Handle graceful shutdown with Ctrl+C

**Then open:** `http://localhost:3000`

### Manual Startup

**Backend (Terminal 1):**
```bash
python backend/main.py
```

**Frontend (Terminal 2):**
```bash
python web-frontend/server.py
```

## API Endpoints

- `GET /` - Health check
- `GET /voices` - Get available voices  
- `POST /transcribe` - Transcribe audio to text
- `WebSocket /stream` - **Real-time streaming conversation**

## 🧪 Testing

Run comprehensive tests:
```bash
python -m pytest tests/ -v
```

Individual test files:
- `tests/test_backend.py` - Backend API tests
- `tests/test_frontend.py` - Frontend server tests  
- `tests/test_audio_pipeline.py` - Complete audio pipeline tests

## 🎯 Usage

### Web Interface
1. **Select a voice** from the dropdown (Rachel, Domi, or Callum)
2. **Click "🎤 Start Recording"** to speak
3. **Speak your message** clearly
4. **Click "⏹️ Stop Recording"** when done
5. **Listen** as the AI responds with streaming audio

### Voice Selection
- **Rachel** - Calm and professional female voice
- **Domi** - Strong and confident female voice  
- **Callum** - Gravelly voice with unsettling edge

## 🔄 How It Works

This voice agent uses **true streaming** for the fastest possible response times:

1. **🎤 Voice Input**: Record your voice → Whisper transcription
2. **🤖 GPT-4 Streaming**: AI generates text in real-time chunks
3. **🔊 TTS Generation**: Text chunks are immediately converted to audio (ElevenLabs/OpenAI)
4. **🎵 Sequential Playback**: Audio chunks play one after another (no overlapping)
5. **⚡ Real-time**: You hear the AI speak as it generates the response

**Result**: Natural, responsive voice conversations with zero text display!

## 📁 Project Structure

```
voice_agent/
├── backend/
│   └── main.py                    # FastAPI backend with WebSocket streaming
├── web-frontend/
│   ├── index.html                 # Voice-only web interface
│   └── server.py                  # Simple HTTP server for frontend
├── modules/
│   ├── llm.py                     # OpenAI GPT-4 streaming integration
│   ├── speechToText.py            # Speech transcription (Whisper local + API)
│   ├── simple_tts.py              # Streaming TTS (ElevenLabs + OpenAI fallback)
│   └── record.py                  # Audio recording utilities
├── tests/
│   ├── __init__.py
│   ├── test_backend.py            # Backend API tests
│   ├── test_frontend.py            # Frontend server tests
│   └── test_audio_pipeline.py     # Complete audio pipeline tests
├── models/                        # Whisper model cache (auto-created)
├── config.py                      # Configuration and voice settings
├── main.py                        # Command-line interface
├── start.py                       # One-command startup script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🔧 Technical Details

### Backend
- **FastAPI** with WebSocket support
- **Port**: 8000
- **Endpoints**: REST API + WebSocket streaming

### Frontend
- **Pure HTML/JavaScript** - No framework dependencies
- **Port**: 3000
- **Features**: Voice recording, real-time audio playback, voice selection

### Models
- **Whisper**: Local faster-whisper model (cached in `models/` folder)
- **Fallback**: OpenAI Whisper API if local model fails
- **TTS**: ElevenLabs (primary) with OpenAI TTS fallback

## 📝 Notes

- The `models/` folder is auto-created for Whisper model caching
- Voice selection uses ElevenLabs free tier voices
- Audio playback is sequential to prevent overlapping
- All audio is streamed in real-time via WebSocket

## 🐛 Troubleshooting

### Audio Not Playing
- **First time**: Click anywhere on the page to enable audio autoplay
- **Browser permissions**: Allow microphone access when prompted
- **Check console**: Open browser DevTools (F12) for error messages

### Backend Not Starting
- **Port 8000 in use**: Kill existing process: `lsof -ti:8000 | xargs kill -9`
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **API keys**: Ensure `.env` file has valid keys

### Frontend Not Loading
- **Port 3000 in use**: Kill existing process: `lsof -ti:3000 | xargs kill -9`
- **Check backend**: Ensure backend is running on port 8000
- **Browser cache**: Try hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

### Transcription Issues
- **Local Whisper fails**: Automatically falls back to OpenAI API
- **Slow transcription**: First run downloads model (~500MB)
- **Model cache**: Stored in `models/` folder (can be deleted to re-download)

## 📦 Dependencies

- **Python 3.8+**
- **OpenAI API key** (for GPT-4 and Whisper fallback)
- **ElevenLabs API key** (for voice synthesis)
- **faster-whisper** (for local speech recognition)
- **FastAPI + Uvicorn** (backend server)
- **WebSockets** (real-time communication)

## 📄 License

This project is for personal/educational use. Ensure you comply with:
- OpenAI API Terms of Service
- ElevenLabs API Terms of Service
- Local data privacy regulations
