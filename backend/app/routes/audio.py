from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.tts_service import text_to_speech
from app.database import engine
from sqlmodel import Session
from app.models import Document
from pathlib import Path

router = APIRouter()

class AudioReq(BaseModel):
    document_id: int
    lang: str = "en"

@router.post("/")
def generate_audio(req: AudioReq):
    with Session(engine) as session:
        doc = session.get(Document, req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_filepath = doc.filepath
        doc_id = doc.id
    summary_path = doc_filepath + ".summary.txt"
    simplified_path = doc_filepath + ".simplified.beginner.txt"
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        try:
            with open(simplified_path, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=400, detail="Summary text not found; run simplify first")
    out = text_to_speech(text, filename_prefix=f"doc_{doc_id}_audio", lang=req.lang)
    return {"audio_path": out, "audio_url": f"/files/outputs/{Path(out).name}"}
