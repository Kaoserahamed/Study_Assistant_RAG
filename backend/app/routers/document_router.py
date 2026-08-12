# app/routers/document_router.py
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

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