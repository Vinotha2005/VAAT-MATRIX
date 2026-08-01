from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.routes import upload, extract, simplify, audio, captions, dashboard, auth, video, quiz
from app.database import init_db
from pathlib import Path
import jwt
import os

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"

app = FastAPI(title="AccessLearn API")
SECRET = os.getenv("JWT_SECRET", "replace_this_in_prod")
PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/auth/login", "/auth/register"}
PUBLIC_PREFIXES = ("/files/")

@app.middleware("http")
async def auth_guard(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES):
        return await call_next(request)

    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Authentication required"})

    token = auth_header.replace("Bearer ", "", 1)
    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(upload.router, prefix="/upload")
app.include_router(extract.router, prefix="/extract")
app.include_router(simplify.router, prefix="/simplify")
app.include_router(audio.router, prefix="/generate-audio")
app.include_router(captions.router, prefix="/generate-captions")
app.include_router(video.router, prefix="/generate-video")
app.include_router(quiz.router, prefix="/generate-quiz")
app.include_router(dashboard.router, prefix="/dashboard")

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/files/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/files/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"service": "AccessLearn backend running"}
