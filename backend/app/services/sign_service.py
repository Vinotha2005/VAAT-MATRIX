import os
from typing import List

# A simple curated mapping of keywords -> sign video file relative to `assets/signs/`
SIGN_LIBRARY = {
    "physics": "physics_sign.mp4",
    "photosynthesis": "photosynthesis_sign.mp4",
    "equation": "equation_sign.mp4",
    "water": "water_sign.mp4",
}

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public", "signs")


def map_keywords_to_signs(text: str) -> List[str]:
    text_low = text.lower()
    clips = []
    for k, v in SIGN_LIBRARY.items():
        if k in text_low:
            path = os.path.join(ASSETS_DIR, v)
            clips.append(path)
    return clips
