from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.sign_service import map_keywords_to_signs
from app.database import engine
from sqlmodel import Session
from app.models import Document

router = APIRouter()

class SignReq(BaseModel):
    document_id: int

@router.post("/")
def generate_sign(req: SignReq):
    with Session(engine) as session:
        doc = session.get(Document, req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
    # read extracted text
    import json
    try:
        with open(doc.filepath + ".json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Document not yet extracted")
    clips = map_keywords_to_signs(data.get("text", ""))
    return {"clips": clips}
