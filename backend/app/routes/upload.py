from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from uuid import uuid4
from app.models import Document
from app.database import engine
from sqlmodel import Session

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")
    uid = str(uuid4())
    filename = f"{uid}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(contents)
    # persist minimal document record
    with Session(engine) as session:
        doc = Document(filename=file.filename, filepath=path)
        session.add(doc)
        session.commit()
        session.refresh(doc)
    return {
        "id": doc.id,
        "filename": doc.filename,
        "download_url": f"/files/uploads/{filename}",
    }
