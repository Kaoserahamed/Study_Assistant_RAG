# app/schemas/document.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class DocumentChunkResponse(BaseModel):
    id: int
    page_number: int
    chunk_index: int
    content: str

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    filename: str
    page_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    chunks: List[DocumentChunkResponse] = []