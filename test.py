import json
from stt import transcribe_audio
from llm import extract_tasks

audio_file = "casual.mp3"

transcript = transcribe_audio(audio_file)
print("=== TRANSCRIPT ===")
print(transcript)

if transcript.startswith("Error"):
    print("\nSTT failed. Check audio file.")
else:
    result = extract_tasks(transcript)
    print("\n=== STRUCTURED OUTPUT ===")
    print(json.dumps(result, indent=2))