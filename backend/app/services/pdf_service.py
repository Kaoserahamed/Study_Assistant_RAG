# app/services/pdf_service.py
import os
import uuid
from fastapi import UploadFile, HTTPException
from app.services.document_processor import DocumentProcessor

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class PDFService:
    @staticmethod
    def save_file(file: UploadFile) -> str:
        """Save uploaded file and validate format"""
        if not DocumentProcessor.is_supported(file.filename):
            supported = DocumentProcessor.get_supported_formats()
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {supported}"
            )
        
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        return file_path
    
    @staticmethod
    def extract_chunks(file_path: str, chunk_size: int = 800, overlap: int = 100):
        """Extract chunks from any supported document format"""
        return DocumentProcessor.process_file(file_path, chunk_size, overlap)
    
    @staticmethod
    def delete_file(file_path: str) -> None:
        if os.path.exists(file_path):
            os.remove(file_path)
