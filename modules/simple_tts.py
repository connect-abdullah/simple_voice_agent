import asyncio
import tempfile
import os
from elevenlabs import ElevenLabs
from config import ELEVENLABS_API_KEY, DEFAULT_VOICE_ID

async def simple_elevenlabs_streamer(queue: asyncio.Queue, play_audio=True):
    """
    Simple ElevenLabs TTS streaming using the regular API.
    Collects text chunks and generates speech when we have enough content.
    """
    print("🔊 Starting ElevenLabs TTS streaming...")
    
    collected_text = ""
    chunk_size = 50  # Generate audio every 50 characters
    
    while True:
        text_chunk = await queue.get()
        if text_chunk is None:  # end signal
            # Generate final audio if there's remaining text
            if collected_text.strip():
                await generate_and_play(collected_text, play_audio)
            break
            
        collected_text += text_chunk
        
        # Generate audio when we have enough text or hit sentence boundaries
        if (len(collected_text) >= chunk_size or 
            text_chunk.endswith('.') or 
            text_chunk.endswith('!') or 
            text_chunk.endswith('?')):
            
            if collected_text.strip():
                await generate_and_play(collected_text, play_audio)
                collected_text = ""

async def generate_and_play(text: str, play_audio: bool):
    """Generate and optionally play audio for the given text."""
    try:
        if play_audio:
            print(f"🎵 Generating audio for: {text[:50]}...")
            
            # Run the synchronous ElevenLabs generation in a thread
            loop = asyncio.get_event_loop()
            import concurrent.futures
            
            def generate_audio():
                client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                audio = client.text_to_speech.convert(
                    voice_id=DEFAULT_VOICE_ID,
                    text=text,
                    model_id="eleven_multilingual_v2"
                )
                return b"".join(audio)  # Convert generator to bytes
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                audio_data = await loop.run_in_executor(executor, generate_audio)
            
            # Play the audio using system command
            def play_audio_sync():
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(audio_data)
                    tmp_path = tmp_file.name
                
                # Play using system command (cross-platform)
                import subprocess
                try:
                    if os.system("which afplay > /dev/null 2>&1") == 0:  # macOS
                        subprocess.run(["afplay", tmp_path], check=True)
                    elif os.system("which mpg123 > /dev/null 2>&1") == 0:  # Linux
                        subprocess.run(["mpg123", tmp_path], check=True)
                    else:
                        print("🔇 No audio player found")
                finally:
                    os.unlink(tmp_path)
            
            await loop.run_in_executor(executor, play_audio_sync)
            
        else:
            print(f"📝 TTS (audio disabled): {text}")
            
    except Exception as e:
        print(f"⚠️  TTS error: {e}")
        print(f"📝 Fallback text: {text}")

# Alternative using OpenAI TTS
async def openai_tts_streamer(queue: asyncio.Queue, play_audio=True):
    """
    OpenAI TTS streaming - collects text and generates speech.
    """
    from openai import OpenAI
    from config import OPENAI_API_KEY
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("🔊 Starting OpenAI TTS streaming...")
    
    collected_text = ""
    chunk_size = 100  # Generate audio every 100 characters
    
    while True:
        text_chunk = await queue.get()
        if text_chunk is None:  # end signal
            # Generate final audio if there's remaining text
            if collected_text.strip():
                await generate_openai_audio(client, collected_text, play_audio)
            break
            
        collected_text += text_chunk
        
        # Generate audio when we have enough text or hit sentence boundaries
        if (len(collected_text) >= chunk_size or 
            text_chunk.endswith('.') or 
            text_chunk.endswith('!') or 
            text_chunk.endswith('?')):
            
            if collected_text.strip():
                await generate_openai_audio(client, collected_text, play_audio)
                collected_text = ""

async def generate_openai_audio(client, text: str, play_audio: bool):
    """Generate and optionally play OpenAI TTS audio."""
    try:
        if play_audio:
            print(f"🎵 Generating OpenAI audio for: {text[:50]}...")
            
            loop = asyncio.get_event_loop()
            import concurrent.futures
            
            def generate_audio():
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=text
                )
                return response.content
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                audio_content = await loop.run_in_executor(executor, generate_audio)
            
            # Save and play audio
            def play_audio_sync():
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(audio_content)
                    tmp_path = tmp_file.name
                
                # Play using system command (cross-platform)
                import subprocess
                try:
                    if os.system("which afplay > /dev/null 2>&1") == 0:  # macOS
                        subprocess.run(["afplay", tmp_path], check=True)
                    elif os.system("which mpg123 > /dev/null 2>&1") == 0:  # Linux
                        subprocess.run(["mpg123", tmp_path], check=True)
                    else:
                        print("🔇 No audio player found")
                finally:
                    os.unlink(tmp_path)
            
            await loop.run_in_executor(executor, play_audio_sync)
            
        else:
            print(f"📝 TTS (audio disabled): {text}")
            
    except Exception as e:
        print(f"⚠️  OpenAI TTS error: {e}")
        print(f"📝 Fallback text: {text}")

# WebSocket versions that send audio data instead of playing locally
async def simple_elevenlabs_streamer_websocket(queue: asyncio.Queue, websocket, voice_id=None):
    """
    ElevenLabs TTS streaming that sends audio data via WebSocket.
    """
    from config import DEFAULT_VOICE_ID
    voice_id = voice_id or DEFAULT_VOICE_ID
    print(f"🔊 Starting ElevenLabs TTS streaming to WebSocket with voice: {voice_id}...")
    
    collected_text = ""
    chunk_size = 50  # Generate audio every 50 characters
    
    while True:
        text_chunk = await queue.get()
        if text_chunk is None:  # end signal
            # Generate final audio if there's remaining text
            if collected_text.strip():
                await generate_and_send_audio(collected_text, websocket, "elevenlabs", voice_id=voice_id)
            break
            
        collected_text += text_chunk
        
        # Generate audio when we have enough text or hit sentence boundaries
        if (len(collected_text) >= chunk_size or 
            text_chunk.endswith('.') or 
            text_chunk.endswith('!') or 
            text_chunk.endswith('?')):
            
            if collected_text.strip():
                await generate_and_send_audio(collected_text, websocket, "elevenlabs", voice_id=voice_id)
                collected_text = ""

async def openai_tts_streamer_websocket(queue: asyncio.Queue, websocket):
    """
    OpenAI TTS streaming that sends audio data via WebSocket.
    """
    from openai import OpenAI
    from config import OPENAI_API_KEY
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("🔊 Starting OpenAI TTS streaming to WebSocket...")
    
    collected_text = ""
    chunk_size = 100  # Generate audio every 100 characters
    
    while True:
        text_chunk = await queue.get()
        if text_chunk is None:  # end signal
            # Generate final audio if there's remaining text
            if collected_text.strip():
                await generate_and_send_audio(collected_text, websocket, "openai", client)
            break
            
        collected_text += text_chunk
        
        # Generate audio when we have enough text or hit sentence boundaries
        if (len(collected_text) >= chunk_size or 
            text_chunk.endswith('.') or 
            text_chunk.endswith('!') or 
            text_chunk.endswith('?')):
            
            if collected_text.strip():
                await generate_and_send_audio(collected_text, websocket, "openai", client)
                collected_text = ""

async def generate_and_send_audio(text: str, websocket, tts_type: str, client=None, voice_id=None):
    """Generate audio and send it via WebSocket."""
    try:
        print(f"🎵 Generating {tts_type} audio for: {text[:50]}...")
        
        loop = asyncio.get_event_loop()
        import concurrent.futures
        import base64
        import json
        
        def generate_audio():
            if tts_type == "elevenlabs":
                from elevenlabs import ElevenLabs
                from config import ELEVENLABS_API_KEY, DEFAULT_VOICE_ID
                
                used_voice_id = voice_id or DEFAULT_VOICE_ID
                elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                audio = elevenlabs_client.text_to_speech.convert(
                    voice_id=used_voice_id,
                    text=text,
                    model_id="eleven_multilingual_v2"
                )
                return b"".join(audio)  # Convert generator to bytes
            else:  # openai
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=text
                )
                return response.content
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            audio_data = await loop.run_in_executor(executor, generate_audio)
        
        # Encode audio data as base64 and send via WebSocket
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        message = json.dumps({
            "type": "audio_chunk",
            "audio_data": audio_b64,
            "text": text
        })
        await websocket.send_text(message)
        
    except Exception as e:
        print(f"⚠️  {tts_type} TTS error: {e}")
        print(f"📝 Fallback text: {text}")
