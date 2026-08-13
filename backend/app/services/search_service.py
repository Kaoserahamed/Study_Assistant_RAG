# app/services/search_service.py
from typing import List, Dict, Any, Optional
import os
from sqlalchemy.orm import Session
from app.services.embedding_service import embedding_service
from app.repositories.document_repository import DocumentRepository
from app.models.document import Document


class SearchService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    @staticmethod
    def _infer_document_kind(filename: str) -> str:
        """Infer document kind from filename
        
        Returns one of: 'slides', 'lecture-notes', 'handout', 'textbook'
        """
        lower = filename.lower()
        if 'slide' in lower or filename.endswith(('.ppt', '.pptx')):
            return 'slides'
        if 'note' in lower or 'lecture' in lower:
            return 'lecture-notes'
        if 'handout' in lower or 'worksheet' in lower or 'problem' in lower:
            return 'handout'
        return 'textbook'  # Default kind

    @staticmethod
    def _parse_document_ids(document_ids: list) -> List[int]:
        """Accept the frontend's ``doc-12`` form without leaking ValueErrors."""
        parsed_ids = []
        for document_id in document_ids or []:
            try:
                value = str(document_id).removeprefix("doc-")
                parsed_ids.append(int(value))
            except (TypeError, ValueError):
                raise ValueError(f"Invalid document id: {document_id!r}")
        return parsed_ids
    
    async def search_documents_async(self, query: str, user_id: int, top_k: int = 20, document_ids: list = None) -> List[Dict[str, Any]]:
        """Search for relevant document chunks using RAG (async)
        
        Args:
            query: Search query text
            user_id: User ID for filtering
            top_k: Number of top results to return (default 10 for better context coverage)
            document_ids: Optional list of document IDs to filter by. If provided, only search in these documents.
        """
        print(f"[SEARCH] Starting async search for: '{query}'")
        print(f"[SEARCH] User ID: {user_id}, Top K: {top_k}")
        
        if document_ids:
            # Convert doc-{id} format to just {id} for the filter
            doc_ids = self._parse_document_ids(document_ids)
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
        results = await embedding_service.search_similar_async(
            query_text=query,
            top_k=top_k,
            filter=filter_criteria
        )
        
        print(f"[SEARCH] Search returned {len(results)} results")
        
        # Format results and fetch document titles from DB if available
        formatted_results = []
        doc_cache = {}  # Cache for document lookups
        results_with_content = 0  # Track how many results have content
        
        for i, match in enumerate(results):
            metadata = match.get("metadata", {})
            doc_id = metadata.get("document_id")
            content = metadata.get("content", "")
            score = match.get("score", 0)
            
            print(f"[SEARCH] Processing result {i+1}:")
            print(f"[SEARCH]   - doc_id: {doc_id}")
            print(f"[SEARCH]   - score: {score:.4f}")
            print(f"[SEARCH]   - content length: {len(content)}")
            print(f"[SEARCH]   - content preview: {content[:80]}..." if content else "[SEARCH]   - NO CONTENT")
            
            # Only include results that have content AND have reasonable similarity scores
            # For cosine similarity: 0.5+ is generally good semantic similarity
            # Scores below 0.3 are likely not semantically related
            if not content or len(content.strip()) < 10:
                print(f"[SEARCH] Skipping result {i+1}: insufficient content")
                continue
            
            min_score = float(os.getenv("RAG_MIN_RELEVANCE_SCORE", "0.35"))
            if score < min_score:
                print(f"[SEARCH] Skipping result {i+1}: score {score:.4f} is below {min_score:.2f}")
                continue
            if score >= 0.5:
                print(f"[SEARCH] GOOD: High relevance score {score:.4f} - strong semantic match")
            
            results_with_content += 1
            
            # Fetch document title from database (with caching)
            doc_title = "Unknown Document"
            if doc_id:
                if doc_id not in doc_cache and self.db:
                    doc = self.db.query(Document).filter(Document.id == doc_id).first()
                    doc_cache[doc_id] = doc.filename if doc else "Unknown Document"
                doc_title = doc_cache.get(doc_id, "Unknown Document")
            
            # Infer document kind from filename
            doc_kind = self._infer_document_kind(doc_title)
            
            result = {
                "id": match.get("id", f"chunk-{doc_id}"),
                "documentId": str(doc_id) if doc_id else "",
                "documentTitle": doc_title,
                "documentKind": doc_kind,
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
            
            print(f"[SEARCH] Result {results_with_content}: {doc_title} (page {result['page']}, score: {result['score']:.3f}, snippet_len: {len(result['snippet'])})")
            formatted_results.append(result)
            
        
        print(f"[SEARCH] Formatted {len(formatted_results)} relevant results for context selection")
        if len(formatted_results) < len(results):
            print(f"[SEARCH] Note: Filtered out {len(results) - len(formatted_results)} results with missing/empty content or low scores")
        
        return formatted_results
    
    def search_documents(self, query: str, user_id: int, top_k: int = 10, document_ids: list = None) -> List[Dict[str, Any]]:
        """Search for relevant document chunks using RAG
        
        Args:
            query: Search query text
            user_id: User ID for filtering
            top_k: Number of top results to return (default 10 for better context coverage)
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
        results_with_content = 0  # Track how many results have content
        
        for i, match in enumerate(results):
            metadata = match.get("metadata", {})
            doc_id = metadata.get("document_id")
            content = metadata.get("content", "")
            score = match.get("score", 0)
            
            print(f"[SEARCH] Processing result {i+1}:")
            print(f"[SEARCH]   - doc_id: {doc_id}")
            print(f"[SEARCH]   - score: {score:.4f}")
            print(f"[SEARCH]   - content length: {len(content)}")
            print(f"[SEARCH]   - content preview: {content[:80]}..." if content else "[SEARCH]   - NO CONTENT")
            
            # Only include results that have content AND have reasonable similarity scores
            # For cosine similarity: 0.5+ is generally good semantic similarity
            # Scores below 0.3 are likely not semantically related
            if not content or len(content.strip()) < 10:
                print(f"[SEARCH] Skipping result {i+1}: insufficient content")
                continue
            
            # Check semantic relevance: warn if score is suspiciously low
            # (might indicate fake embeddings or poor semantic search)
            if score < 0.3:
                print(f"[SEARCH] WARNING: Low relevance score {score:.4f} - verify embedding quality")
            
            results_with_content += 1
            
            # Fetch document title from database (with caching)
            doc_title = "Unknown Document"
            if doc_id:
                if doc_id not in doc_cache and self.db:
                    doc = self.db.query(Document).filter(Document.id == doc_id).first()
                    doc_cache[doc_id] = doc.filename if doc else "Unknown Document"
                doc_title = doc_cache.get(doc_id, "Unknown Document")
            
            # Infer document kind from filename
            doc_kind = self._infer_document_kind(doc_title)
            
            result = {
                "id": match.get("id", f"chunk-{doc_id}"),
                "documentId": str(doc_id) if doc_id else "",
                "documentTitle": doc_title,
                "documentKind": doc_kind,
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
            
            print(f"[SEARCH] Result {results_with_content}: {doc_title} (page {result['page']}, score: {result['score']:.3f}, snippet_len: {len(result['snippet'])})")
            formatted_results.append(result)
            
            # Stop after getting 5 quality results
            if results_with_content >= 5:
                break
        
        print(f"[SEARCH] Formatted {len(formatted_results)} results with content for LLM context")
        if len(formatted_results) < len(results):
            print(f"[SEARCH] Note: Filtered out {len(results) - len(formatted_results)} results with missing/empty content")
        
        return formatted_results


search_service = SearchService()
