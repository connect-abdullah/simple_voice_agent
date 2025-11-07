from modules.record import record_audio, save_temp_wav
from modules.speechToText import transcribe_audio
from modules.llm import generate_reply
from modules.textToSpeech import speak_text

def main():
    print("🎧 Voice Agent Ready. Say 'exit' to quit.\n")

    while True:
        audio = record_audio(duration=5)
        file_path = save_temp_wav(audio)
        text = transcribe_audio(file_path)
        print(f"🧍 You: {text}")

        if text.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        reply = generate_reply(text)

        print(f"🤖 AI: {reply}")
        speak_text(reply)

if __name__ == "__main__":
    main()
