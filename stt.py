from faster_whisper import WhisperModel
import tempfile

model = WhisperModel("tiny")

def clean_text(text):
    fillers = ["uh", "um", "you know"]
    for f in fillers:
        text = text.replace(f, "")
    return text

def transcribe_audio(audio_path):
    try:
        segments, _ = model.transcribe(audio_path)

        text = ""
        for segment in segments:
            text += segment.text + " "

        return clean_text(text.strip())

    except Exception:
        return "Error"

def save_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
        temp.write(uploaded_file.read())
        return temp.name

