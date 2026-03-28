import tempfile
import streamlit as st
from faster_whisper import WhisperModel

@st.cache_resource
def load_model():
    return WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8"
    )

def clean_text(text):
    fillers = ["uh", "um", "you know"]
    for f in fillers:
        text = text.replace(f, "")
    return " ".join(text.split())

def transcribe_audio(audio_path):
    try:
        model = load_model()

        segments, _ = model.transcribe(
            audio_path,
            beam_size=1,
            vad_filter=True
        )

        text_parts = []
        for segment in segments:
            text_parts.append(segment.text.strip())

        full_text = " ".join(text_parts).strip()
        return clean_text(full_text)

    except Exception as e:
        return f"Error: {str(e)}"

def save_uploaded_file(uploaded_file):
    suffix = ".mp3"
    if "." in uploaded_file.name:
        suffix = "." + uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(uploaded_file.read())
        return temp.name
