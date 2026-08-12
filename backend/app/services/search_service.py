# app/services/search_service.py
from typing import List, Dict, Any
from app.services.embedding_service import embedding_service


class SearchService:
    
    @staticmethod
    def search_documents(query: str, user_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant document chunks using RAG"""
        # Filter by user_id to ensure user only sees their documents
        filter_criteria = {"user_id": {"$eq": user_id}}
        
        results = embedding_service.search_similar(
            query_text=query,
            top_k=top_k,
            filter=filter_criteria
        )
        
        # Format results
        formatted_results = []
        for match in results:
            formatted_results.append({
                "chunk_id": match.get("id"),
                "score": match.get("score"),
                "document_id": match.get("metadata", {}).get("document_id"),
                "chunk_index": match.get("metadata", {}).get("chunk_index"),
                "page_number": match.get("metadata", {}).get("page_number"),
                "content": match.get("metadata", {}).get("content")
            })
        
        return formatted_results


search_service = SearchService()
