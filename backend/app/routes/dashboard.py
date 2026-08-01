import json
from fastapi import APIRouter, HTTPException
from app.database import engine
from sqlmodel import Session
from app.models import Document
from pathlib import Path
from app.services.ai_service import summarize_text

router = APIRouter()

@router.get("/{doc_id}")
def get_dashboard(doc_id: int):
    with Session(engine) as session:
        doc = session.get(Document, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
    # compile available outputs
    outputs = {}
    base = Path(doc.filepath)
    if base.with_suffix(base.suffix + ".json").exists():
        outputs["extracted"] = f"/files/uploads/{base.name}.json"
    if base.with_suffix(base.suffix + ".simplified.beginner.txt").exists():
        outputs["simplified_beginner"] = f"/files/uploads/{base.name}.simplified.beginner.txt"
    audio_path = base.parent.parent / "outputs" / f"doc_{doc.id}_audio.mp3"
    if audio_path.exists():
        outputs["audio"] = f"/files/outputs/{audio_path.name}"
    video_path = base.parent.parent / "outputs" / f"doc_{doc.id}_video.mp4"
    if video_path.exists():
        outputs["video"] = f"/files/outputs/{video_path.name}"
    if base.with_suffix(base.suffix + ".srt").exists():
        outputs["captions"] = f"/files/uploads/{base.name}.srt"

    summary_text = ""
    summary_path = base.with_suffix(base.suffix + ".summary.txt")
    extracted_path = base.with_suffix(base.suffix + ".json")
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_text = f.read().strip()
        if summary_text.endswith("...") and extracted_path.exists():
            with open(extracted_path, "r", encoding="utf-8") as f:
                extracted_data = json.load(f)
            summary_text = summarize_text(extracted_data.get("text", "")).get("summary", "")
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary_text)
    elif extracted_path.exists():
        with open(extracted_path, "r", encoding="utf-8") as f:
            extracted_data = json.load(f)
        summary_text = summarize_text(extracted_data.get("text", "")).get("summary", "")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)
    if not summary_text and base.with_suffix(base.suffix + ".simplified.beginner.txt").exists():
        with open(base.with_suffix(base.suffix + ".simplified.beginner.txt"), "r", encoding="utf-8") as f:
            summary_text = summarize_text(f.read()).get("summary", "")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

    return {
        "document": {"id": doc.id, "filename": doc.filename},
        "outputs": outputs,
        "summary_text": summary_text,
    }
