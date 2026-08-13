# app/controllers/document_controller.py
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import os
from app.services.document_service import DocumentService

class DocumentController:
    def __init__(self, db: Session):
        self.service = DocumentService(db)

    async def upload_document_async(self, file: UploadFile, current_user: dict):
        """Upload document with async processing"""
        return await self.service.process_and_save_document_async(file, current_user["id"])

    def upload_document(self, file: UploadFile, current_user: dict):
        """Upload document (sync wrapper - deprecated, use upload_document_async)"""
        return self.service.process_and_save_document(file, current_user["id"])

    def get_documents(self, current_user: dict):
        return self.service.list_user_documents(current_user["id"])

    def get_document_by_id(self, document_id: int, current_user: dict):
        return self.service.get_document_details(document_id, current_user["id"])

    def get_document_file_path(self, document_id: int, current_user: dict) -> str:
        """Get the file path for a document, checking authorization"""
        doc = self.service.get_document_details(document_id, current_user["id"])
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path = doc["file_path"]
        
        # Convert relative path to absolute path if needed
        if not os.path.isabs(file_path):
            # Get backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(backend_dir, file_path)
        
        return file_path

    def delete_document(self, document_id: int, current_user: dict):
        self.service.delete_document(document_id, current_user["id"])