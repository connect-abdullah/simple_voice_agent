import asyncio
import concurrent.futures
import base64
import json
from elevenlabs import ElevenLabs
from config import ELEVENLABS_API_KEY, DEFAULT_VOICE_ID

async def simple_elevenlabs_streamer_websocket(queue: asyncio.Queue, websocket, voice_id=None):
    """
    ElevenLabs TTS streaming that sends audio data via WebSocket.
    """
    voice_id = voice_id or DEFAULT_VOICE_ID
    print(f"🔊 Starting ElevenLabs TTS with voice: {voice_id}")
    
    collected_text = ""
    chunk_size = 55
    
    while True:
        text_chunk = await queue.get()
        if text_chunk is None:
            if collected_text.strip():
                await generate_and_send_audio(collected_text, websocket, voice_id)
            break
            
        collected_text += text_chunk
        
        if (len(collected_text) >= chunk_size or 
            text_chunk.endswith('.') or 
            text_chunk.endswith('!') or 
            text_chunk.endswith('?')):
            
            if collected_text.strip():
                await generate_and_send_audio(collected_text, websocket, voice_id)
                collected_text = ""

async def generate_and_send_audio(text: str, websocket, voice_id: str):
    """Generate audio with ElevenLabs and send via WebSocket."""
    try:
        print(f"🎵 Generating audio: {text[:50]}...")
        
        loop = asyncio.get_event_loop()
        
        def generate_audio():
            client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            audio = client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_multilingual_v2"
            )
            return b"".join(audio)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            audio_data = await loop.run_in_executor(executor, generate_audio)
        
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        print(f"✅ Audio generated: {len(audio_data)} bytes")
        
        message = json.dumps({
            "type": "audio_chunk",
            "audio_data": audio_b64,
            "text": text
        })
        await websocket.send_text(message)
        
    except Exception as e:
        print(f"❌ TTS error: {e}")
        import traceback
        traceback.print_exc()
