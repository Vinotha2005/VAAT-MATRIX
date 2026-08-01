from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import engine
from sqlmodel import Session, select
from app.models import User
import hashlib
import jwt
import os

SECRET = os.getenv("JWT_SECRET", "replace_this_in_prod")

router = APIRouter()

class RegisterReq(BaseModel):
    email: str
    password: str

class LoginReq(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(req: RegisterReq):
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == req.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        hashed = hashlib.sha256(req.password.encode()).hexdigest()
        user = User(email=req.email, hashed_password=hashed)
        session.add(user)
        session.commit()
        session.refresh(user)
    token = jwt.encode({"user_id": user.id}, SECRET, algorithm="HS256")
    return {"token": token}

@router.post("/login")
def login(req: LoginReq):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == req.email)).first()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        hashed = hashlib.sha256(req.password.encode()).hexdigest()
        if hashed != user.hashed_password:
            raise HTTPException(status_code=400, detail="Invalid credentials")
    token = jwt.encode({"user_id": user.id}, SECRET, algorithm="HS256")
    return {"token": token}
