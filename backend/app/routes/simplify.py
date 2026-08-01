from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ai_service import simplify_text, summarize_text
from app.database import engine
from sqlmodel import Session
from app.models import Document
from pathlib import Path

router = APIRouter()

class SimplifyRequest(BaseModel):
    document_id: int
    level: str = "beginner"

@router.post("/")
def simplify(req: SimplifyRequest):
    with Session(engine) as session:
        doc = session.get(Document, req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_filepath = doc.filepath
    # load extracted text
    import json
    extracted_path = doc_filepath + ".json"
    try:
        with open(extracted_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Document not yet extracted")
    simplified = simplify_text(data.get("text", ""), level=req.level)
    summary = summarize_text(data.get("text", ""))
    out_path = doc_filepath + f".simplified.{req.level}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(simplified.get("simplified", ""))
    summary_path = doc_filepath + ".summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary.get("summary", ""))
    return {
        "simplified_path": out_path,
        "simplified_url": f"/files/uploads/{Path(out_path).name}",
        "summary_path": summary_path,
        "summary_url": f"/files/uploads/{Path(summary_path).name}",
        "summary_text": summary.get("summary", ""),
    }
