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
        
        unique_filename = f"{uuid.uuid4()}_{os.path.basename(file.filename)}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        return file_path
    
    @staticmethod
    def extract_chunks(file_path: str, chunk_size: int = 1400, overlap: int = 200):
        """Extract chunks from any supported document format
        
        Args:
            file_path: Path to the document
            chunk_size: Size of each chunk in characters (default 1400 - about 220-280 words)
            overlap: Overlap between chunks (default 200 chars)
            
        Moderate chunks preserve topic focus while the overlap keeps sentences at chunk boundaries retrievable.
        """
        return DocumentProcessor.process_file(file_path, chunk_size, overlap)
    
    @staticmethod
    def delete_file(file_path: str) -> None:
        if os.path.exists(file_path):
            os.remove(file_path)
