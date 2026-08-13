# app/services/search_service.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.embedding_service import embedding_service
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document


class SearchService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    def search_documents(self, query: str, user_id: int, top_k: int = 5, document_ids: list = None) -> List[Dict[str, Any]]:
        """Search for relevant document chunks using RAG
        
        Args:
            query: Search query text
            user_id: User ID for filtering
            top_k: Number of top results to return
            document_ids: Optional list of document IDs to filter by. If provided, only search in these documents.
        """
        print(f"[SEARCH] Starting search for: '{query}'")
        print(f"[SEARCH] User ID: {user_id}, Top K: {top_k}")
        
        if document_ids:
            # Convert doc-{id} format to just {id} for the filter
            doc_ids = [int(doc_id.replace("doc-", "")) if isinstance(doc_id, str) else doc_id for doc_id in document_ids]
            print(f"[SEARCH] Filtering by documents: {doc_ids}")
            # Pinecone filter for specific documents
            filter_criteria = {
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"document_id": {"$in": doc_ids}}
                ]
            }
        else:
            # Filter by user_id only to ensure user only sees their documents
            print(f"[SEARCH] No document filter, searching all user documents")
            filter_criteria = {"user_id": {"$eq": user_id}}
        
        print(f"[SEARCH] Applying filter: {filter_criteria}")
        results = embedding_service.search_similar(
            query_text=query,
            top_k=top_k,
            filter=filter_criteria
        )
        
        print(f"[SEARCH] Search returned {len(results)} results")
        
        # Format results and fetch document titles from DB if available
        formatted_results = []
        doc_cache = {}  # Cache for document lookups
        
        for i, match in enumerate(results):
            metadata = match.get("metadata", {})
            doc_id = metadata.get("document_id")
            content = metadata.get("content", "")
            
            print(f"[SEARCH] Processing result {i+1}:")
            print(f"[SEARCH]   - doc_id: {doc_id}")
            print(f"[SEARCH]   - content length: {len(content)}")
            print(f"[SEARCH]   - content preview: {content[:80]}..." if content else "[SEARCH]   - NO CONTENT")
            
            # Fetch document title from database (with caching)
            doc_title = "Unknown Document"
            if doc_id:
                if doc_id not in doc_cache and self.db:
                    doc = self.db.query(Document).filter(Document.id == doc_id).first()
                    doc_cache[doc_id] = doc.filename if doc else "Unknown Document"
                doc_title = doc_cache.get(doc_id, "Unknown Document")
            
            result = {
                "id": match.get("id", f"chunk-{doc_id}"),
                "documentId": str(doc_id) if doc_id else "",
                "documentTitle": doc_title,
                "documentKind": "document",
                "page": metadata.get("page_number", 1),
                "snippet": content,  # This is what gets passed to LLM
                # Keep original fields for backward compatibility
                "chunk_id": match.get("id"),
                "score": match.get("score"),
                "document_id": doc_id,
                "chunk_index": metadata.get("chunk_index"),
                "page_number": metadata.get("page_number"),
                "content": content
            }
            
            print(f"[SEARCH] Result {i+1}: {doc_title} (page {result['page']}, score: {result['score']:.3f}, snippet_len: {len(result['snippet'])})")
            formatted_results.append(result)
        
        print(f"[SEARCH] Formatted {len(formatted_results)} results for LLM context")
        return formatted_results


search_service = SearchService()
