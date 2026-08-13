# app/routers/document_router.py
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import mimetypes

from app.database import get_db
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.controllers.document_controller import DocumentController
from app.auth import get_current_user
from app.services.document_processor import SUPPORTED_FORMATS

router = APIRouter(prefix="/documents", tags=["Documents"])

# Allowed file types and size limits
ALLOWED_EXTENSIONS = SUPPORTED_FORMATS
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_file(file: UploadFile) -> None:
    """Validate file type and size"""
    # Check file extension
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    
    # Note: file.size is not always available, will check during processing
    # The actual size check happens when reading the file


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process document asynchronously"""
    # Validate file before processing
    validate_file(file)
    
    controller = DocumentController(db)
    return await controller.upload_document_async(file, current_user)

@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    controller = DocumentController(db)
    return controller.get_documents(current_user)

# IMPORTANT: /file endpoint must come BEFORE /{document_id} to avoid route conflict
@router.get("/{document_id}/file")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Download an owned document with its actual content type."""
    try:
        from app.models.document import Document
        doc = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user["id"],
        ).first()
        
        if not doc:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path = doc.file_path
        
        # Convert relative path to absolute if needed
        if not os.path.isabs(file_path):
            current_file = os.path.abspath(__file__)
            app_dir = os.path.dirname(os.path.dirname(current_file))
            backend_dir = os.path.dirname(app_dir)
            file_path = os.path.join(backend_dir, file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=file_path,
            media_type=mimetypes.guess_type(doc.filename)[0] or "application/octet-stream",
            filename=os.path.basename(file_path),
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
            }
        )
        
    except Exception as e:
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# This must come AFTER the /file endpoint
@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document_by_id(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    controller = DocumentController(db)
    return controller.get_document_by_id(document_id, current_user)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    controller = DocumentController(db)
    controller.delete_document(document_id, current_user)
    return None
