from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.caption_service import generate_srt_from_text
from app.database import engine
from sqlmodel import Session
from app.models import Document
from pathlib import Path

router = APIRouter()

class CaptionReq(BaseModel):
    document_id: int

@router.post("/")
def generate_captions(req: CaptionReq):
    with Session(engine) as session:
        doc = session.get(Document, req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_filepath = doc.filepath
    simplified_path = doc_filepath + ".simplified.beginner.txt"
    try:
        with open(simplified_path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Simplified text not found; run simplify first")
    srt = generate_srt_from_text(text)
    out_path = doc_filepath + ".srt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(srt)
    return {"srt_path": out_path, "srt_url": f"/files/uploads/{Path(out_path).name}"}
