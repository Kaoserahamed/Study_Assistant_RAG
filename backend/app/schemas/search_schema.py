# app/schemas/search_schema.py
from pydantic import BaseModel
from typing import List, Optional


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


class SearchResult(BaseModel):
    chunk_id: str
    score: float
    document_id: int
    chunk_index: int
    page_number: int
    content: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
