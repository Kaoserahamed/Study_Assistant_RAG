# app/repositories/document_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.document import Document

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, filename: str, file_path: str, page_count: int) -> Document:
        doc = Document(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            page_count=page_count
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_all_by_user(self, user_id: int) -> List[Document]:
        return self.db.query(Document).filter(Document.user_id == user_id).all()

    def get_by_id(self, document_id: int, user_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()

    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()