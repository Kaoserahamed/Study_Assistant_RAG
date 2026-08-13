# app/routers/document_router.py
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status, Header
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.controllers.document_controller import DocumentController
from app.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    controller = DocumentController(db)
    return controller.upload_document(file, current_user)

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
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    """Download/serve the document file - manual auth validation"""
    try:
        # Validate authorization header
        if not authorization:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        try:
            scheme, token = authorization.split(" ")
            if scheme.lower() != "bearer":
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        except ValueError:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        # Get document from database
        from app.models.document import Document
        doc = db.query(Document).filter(Document.id == document_id).first()
        
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
            media_type="application/pdf",
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