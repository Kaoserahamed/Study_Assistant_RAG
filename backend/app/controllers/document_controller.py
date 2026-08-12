# app/controllers/document_controller.py
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.services.document_service import DocumentService

class DocumentController:
    def __init__(self, db: Session):
        self.service = DocumentService(db)

    def upload_document(self, file: UploadFile, current_user: dict):
        return self.service.process_and_save_document(file, current_user["id"])

    def get_documents(self, current_user: dict):
        return self.service.list_user_documents(current_user["id"])

    def get_document_by_id(self, document_id: int, current_user: dict):
        return self.service.get_document_details(document_id, current_user["id"])

    def delete_document(self, document_id: int, current_user: dict):
        self.service.delete_document(document_id, current_user["id"])