# app/repositories/chunk_repository.py
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.chunk import DocumentChunk

class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, document_id: int, chunks_data: List[Dict[str, Any]]) -> None:
        chunk_objects = [
            DocumentChunk(
                document_id=document_id,
                content=c["content"],
                page_number=c["page_number"],
                chunk_index=c["chunk_index"]
            )
            for c in chunks_data
        ]
        self.db.bulk_save_objects(chunk_objects)
        self.db.commit()