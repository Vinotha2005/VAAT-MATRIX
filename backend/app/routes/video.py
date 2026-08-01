import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import engine
from sqlmodel import Session
from app.models import Document
from app.services.ai_service import summarize_text
from app.services.video_service import recommend_youtube_videos
import os
from pathlib import Path

router = APIRouter()

class VideoReq(BaseModel):
    document_id: int

@router.post("/")
def generate_video(req: VideoReq):
    with Session(engine) as session:
        doc = session.get(Document, req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_filepath = doc.filepath
    simplified = doc_filepath + ".simplified.beginner.txt"
    extracted = doc_filepath + ".json"
    text_source = ""

    if os.path.exists(extracted):
        with open(extracted, 'r', encoding='utf-8') as f:
            extracted_data = json.load(f)
        text_source = extracted_data.get("text", "")

    if not text_source and os.path.exists(simplified):
        with open(simplified, 'r', encoding='utf-8') as f:
            text_source = f.read()

    if not text_source:
        raise HTTPException(status_code=400, detail="No extracted or simplified text available")

    recommendations = recommend_youtube_videos(text_source)
    summary = summarize_text(text_source)
    return {
        "youtube_recommendations": recommendations,
        "summary": summary.get("summary", ""),
        "summary_text": summary.get("summary", ""),
    }
