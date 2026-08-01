import os
from sqlmodel import SQLModel, create_engine, Session
from app.models import User, Document, ProcessingJob

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/accesslearn")
if DATABASE_URL.startswith("postgres") and (os.getenv("LOCAL_DEV", "0") == "1" or os.name == "nt"):
    DATABASE_URL = "sqlite:///./accesslearn.db"
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
