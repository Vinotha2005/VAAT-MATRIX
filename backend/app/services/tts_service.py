from gtts import gTTS
import os
from pathlib import Path

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def text_to_speech(text: str, filename_prefix: str = "tts", lang: str = "en") -> str:
    """Generates an MP3 using gTTS and returns path."""
    fname = f"{filename_prefix}.mp3"
    out_path = os.path.join(OUTPUT_DIR, fname)
    tts = gTTS(text=text, lang=lang)
    tts.save(out_path)
    return out_path
