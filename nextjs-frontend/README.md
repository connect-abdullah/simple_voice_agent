# Voice Agent - Next.js Frontend

A modern, beautiful Next.js frontend for the Voice Agent application.

## Features

- 🎤 Voice recording with visual feedback
- 🤖 Real-time AI streaming responses
- 🔊 Multiple ElevenLabs voice options
- 📝 Live transcription display
- 🎨 Modern UI with Tailwind CSS
- ⚡ Fast and responsive

## Getting Started

### Development Mode

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Prerequisites

Make sure the backend API is running on `http://localhost:8000`:

```bash
cd ..
python start.py
```

## Tech Stack

- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **WebSocket** - Real-time communication

## Configuration

The API and WebSocket URLs are configured in `components/VoiceAgent.tsx`:

```typescript
const API_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/stream';
```

Change these if your backend runs on a different port.
