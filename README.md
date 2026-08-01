
# AccessLearn — Accessible Multimodal Learning Platform

A scaffolded full-stack project (backend: FastAPI, frontend: React+TS, DB: PostgreSQL) that converts uploaded PDFs into simplified text, audio (MP3), captions (SRT), and maps keywords to sign-language clips.

Quick start (Docker):

1. Copy `.env.example` values into `backend/.env` and set `OPENAI_API_KEY` and `JWT_SECRET`.
2. Build and run with Docker Compose:

```bash
docker-compose up --build
```

3. Frontend available at `http://localhost:5173`, backend at `http://localhost:8000`.

Notes
- PDF extraction uses PyMuPDF and falls back to pdfplumber + Tesseract for OCR.
- AI simplification has a placeholder in `app/services/ai_service.py`—replace with your OpenAI/Azure call.
- TTS uses `gTTS` to generate MP3s. For production use a managed TTS (Polly/Google Cloud/ Azure) for better control.

Folder structure
- `backend/` — FastAPI app and services
- `frontend/` — React + TypeScript app (Vite)

Next steps to production hardening:
 - Use proper secrets (do not store in repo), configure S3 or object storage for files.
 - Add background workers (Celery/RQ) for CPU-bound tasks.

Video generation
 - Endpoint: `POST /generate-video/` — takes `document_id` and returns a generated MP4 path.
 - Pipeline: creates PNG slides from simplified text, uses existing TTS MP3 and SRT captions, composes MP4 with `ffmpeg`.
 - Docker: backend image includes `ffmpeg` so composition runs inside the container.
- Secure endpoints and implement RBAC.
- Add CI for tests and container scanning.

If you want, I can now:
- Run the Docker compose locally and verify services start.
- Add GitHub Actions workflow for CI/deploy.
- Implement OpenAI integration for better simplification.
