import asyncio
from modules.record import record_audio, save_temp_wav
from modules.speechToText import transcribe_audio
from modules.llm import gpt_stream_to_queue
from modules.simple_tts import simple_elevenlabs_streamer, openai_tts_streamer
from config import OPENAI_API_KEY

async def main():
    print("🎧 Voice Agent Ready (Streaming Mode). Say 'exit' to quit.\n")

    while True:
        audio = record_audio(duration=5)
        file_path = save_temp_wav(audio)
        text = transcribe_audio(file_path)
        print(f"🧍 You: {text}")

        if text.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        print("🤖 AI: ", end="", flush=True)
        
        # Create queue for streaming text chunks
        text_queue = asyncio.Queue()
        
        # Start both streaming tasks concurrently
        gpt_task = asyncio.create_task(gpt_stream_to_queue(text, text_queue))
        
        # Try ElevenLabs first, fallback to OpenAI TTS
        try:
            tts_task = asyncio.create_task(simple_elevenlabs_streamer(text_queue))
        except Exception as e:
            print(f"⚠️  ElevenLabs not available, using OpenAI TTS: {e}")
            tts_task = asyncio.create_task(openai_tts_streamer(text_queue))
        
        # Wait for both tasks to complete
        await asyncio.gather(gpt_task, tts_task)
        print("\n")  # New line after streaming completes

if __name__ == "__main__":
    asyncio.run(main())
