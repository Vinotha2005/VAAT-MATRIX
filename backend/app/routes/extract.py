from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.pdf_service import extract_text
from app.database import engine
from sqlmodel import Session
from app.models import Document, ProcessingJob
from pathlib import Path
from datetime import datetime

router = APIRouter()

class ExtractRequest(BaseModel):
    document_id: int

@router.post("/")
def extract(req: ExtractRequest):
    with Session(engine) as session:
        doc = session.get(Document, req.document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        # capture attributes to avoid detached-instance issues
        doc_id = doc.id
        doc_filepath = doc.filepath
        job = ProcessingJob(document_id=doc.id, status="extracting")
        session.add(job)
        session.commit()
        session.refresh(job)
        job_id = job.id
    # perform extraction
    data = extract_text(doc_filepath)
    # write output to outputs folder
    out_path = doc_filepath + ".json"
    import json
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    with Session(engine) as session:
        job = session.get(ProcessingJob, job_id)
        job.status = "extracted"
        job.result_path = out_path
        job.updated_at = datetime.utcnow()
        session.add(job)
        doc = session.get(Document, doc_id)
        doc.processed = True
        session.add(doc)
        session.commit()
    return {"job_id": job_id, "result": out_path, "result_url": f"/files/uploads/{Path(out_path).name}"}
