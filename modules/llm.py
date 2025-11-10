from openai import OpenAI
import asyncio
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

async def gpt_stream_to_queue(user_input: str, queue: asyncio.Queue):
    """
    Stream GPT response and push text chunks into an asyncio queue in real-time.
    """
    import concurrent.futures
    
    def create_stream():
        """Create the OpenAI stream"""
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}],
            stream=True
        )
    
    # Create the stream in a thread
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        stream = await loop.run_in_executor(executor, create_stream)
        
        # Process chunks in real-time
        def get_next_chunk():
            try:
                return next(stream)
            except StopIteration:
                return None
        
        while True:
            chunk = await loop.run_in_executor(executor, get_next_chunk)
            if chunk is None:
                break
                
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                await queue.put(content)

    # Signal the TTS stream to end
    await queue.put(None)
