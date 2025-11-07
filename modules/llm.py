import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_reply(user_input, context=None):
    messages = []
    if context:
        messages.extend(context)
    messages.append({"role": "user", "content": user_input})

    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = completion.choices[0].message.content.strip()
    return reply
