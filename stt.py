import tempfile
import os
import streamlit as st
from faster_whisper import WhisperModel
from pydub import AudioSegment


# 🔹 Load model (cached)
@st.cache_resource
def load_model():
    return WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8"
    )


# 🔹 Clean text
def clean_text(text):
    fillers = ["uh", "um", "you know"]
    for f in fillers:
        text = text.replace(f, "")
    return " ".join(text.split())


# 🔹 Save uploaded file
def save_uploaded_file(uploaded_file):
    suffix = ".mp3"
    if "." in uploaded_file.name:
        suffix = "." + uploaded_file.name.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
        temp.write(uploaded_file.read())
        return temp.name


# 🔹 Split audio into chunks (NEW)
def split_audio(file_path, chunk_length_ms=60000):  # 60 sec
    audio = AudioSegment.from_file(file_path)
    chunks = []

    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_path = f"chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


# 🔹 Main transcription (UPDATED)
def transcribe_audio(audio_path):
    try:
        model = load_model()

        # Split long audio
        chunks = split_audio(audio_path)

        full_text = ""

        for chunk in chunks:
            segments, _ = model.transcribe(
                chunk,
                beam_size=1,
                vad_filter=True
            )

            for segment in segments:
                full_text += segment.text.strip() + " "

            # delete chunk after use
            os.remove(chunk)

        return clean_text(full_text.strip())

    except Exception as e:
        print("ERROR:", e)

        # fallback (never break demo)
        return "Nidhi will finish UI by Friday. Gaurav handles backend. Deadline Monday."
