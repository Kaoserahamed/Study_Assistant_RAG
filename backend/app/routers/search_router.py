# app/routers/search_router.py
from fastapi import APIRouter, Depends, status
from app.controllers.search_controller import search_controller
from app.schemas.search_schema import SearchRequest, SearchResponse
from app.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/documents", response_model=SearchResponse, status_code=status.HTTP_200_OK)
def search_documents(
    query_request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Search through user's uploaded documents using semantic search"""
    return search_controller.search_documents(query_request, current_user["id"])
