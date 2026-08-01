import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.database import engine
from app.models import Document
from app.services.quiz_service import generate_quiz

router = APIRouter()


class QuizReq(BaseModel):
    document_id: int


@router.post("/")
def create_quiz(req: QuizReq):
    with Session(engine) as session:
        doc = session.get(Document, req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_filepath = doc.filepath

    extracted = doc_filepath + ".json"
    summary_path = doc_filepath + ".summary.txt"
    simplified = doc_filepath + ".simplified.beginner.txt"
    text_source = ""

    if os.path.exists(extracted):
        with open(extracted, "r", encoding="utf-8") as f:
            extracted_data = json.load(f)
        text_source = extracted_data.get("text", "")

    if not text_source and os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            text_source = f.read()

    if not text_source and os.path.exists(simplified):
        with open(simplified, "r", encoding="utf-8") as f:
            text_source = f.read()

    if not text_source:
        raise HTTPException(status_code=400, detail="No extracted, summary, or simplified text available")

    quiz = generate_quiz(text_source)
    return {
        "quiz": quiz["questions"],
        "quiz_url": f"/files/uploads/{Path(doc_filepath).name}.quiz.json",
    }
