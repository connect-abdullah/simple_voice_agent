from typing import Iterable
from openai import OpenAI
import asyncio
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# Future proof function
async def gpt_stream_to_queue(user_input: str, queue: asyncio.Queue):
    """
    Stream GPT response and push text chunks into a single asyncio queue.
    """
    await gpt_stream_to_queues(user_input, [queue])

async def gpt_stream_to_queues(user_input: str, queues: Iterable[asyncio.Queue]):
    """
    Stream GPT response and fan out text chunks to multiple asyncio queues.
    Each queue receives the same content along with the terminating None sentinel.
    """
    import concurrent.futures

    def create_stream():
        """Create the OpenAI stream"""
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}],
            stream=True
        )

    loop = asyncio.get_event_loop()
    queues = list(queues)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        stream = await loop.run_in_executor(executor, create_stream)

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
                for queue in queues:
                    await queue.put(content)

    for queue in queues:
        await queue.put(None)
