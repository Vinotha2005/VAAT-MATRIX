from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    filepath: str
    owner_id: Optional[int] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = Field(default=False)

class ProcessingJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int
    status: str = Field(default="pending")
    result_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
