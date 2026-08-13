# app/services/embedding_service.py
from typing import List
import os
import hashlib
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "student-assistant")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable not set")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = None

def _ensure_index_exists():
    global index
    try:
        # Try to get index info
        pc.describe_index(PINECONE_INDEX_NAME)
        index = pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        print(f"Note: Could not access Pinecone index. Error: {str(e)}")
        # Don't fail - continue without embeddings for now
        index = pc.Index(PINECONE_INDEX_NAME)


def _generate_embedding_from_text(text: str) -> List[float]:
    """Generate a simple embedding from text using hashing
    
    In production, use OpenAI, Hugging Face, or other embedding services.
    This generates a 1024-dimensional vector to match Pinecone index.
    """
    # Simple hash-based embedding for demonstration
    # Each character contributes to specific dimensions
    embedding = [0.0] * 1024
    
    # Use hash to seed deterministic values
    hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
    
    # Create embedding by distributing hash values
    for i, char in enumerate(text[:1024]):
        embedding[i % 1024] += (ord(char) / 256.0) * 0.1
    
    # Normalize
    norm = sum(x**2 for x in embedding) ** 0.5
    if norm > 0:
        embedding = [x / norm for x in embedding]
    
    return embedding


class EmbeddingService:
    
    @staticmethod
    def _get_index():
        global index
        if index is None:
            _ensure_index_exists()
        return index
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generate embedding for a single text"""
        return _generate_embedding_from_text(text)
    
    @staticmethod
    def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """Generate multiple embeddings at once"""
        if not texts:
            return []
        
        return [_generate_embedding_from_text(text) for text in texts]
    
    @staticmethod
    def upsert_to_pinecone(vectors: List[dict]) -> None:
        """Store vectors in Pinecone index
        
        vectors format: [
            {
                "id": "chunk_1",
                "values": [0.1, 0.2, ...],
                "metadata": {"document_id": 1, "chunk_index": 0, "content": "..."}
            }
        ]
        """
        if not vectors:
            return
        
        idx = EmbeddingService._get_index()
        if idx:
            try:
                idx.upsert(vectors=vectors)
            except Exception as e:
                print(f"Warning: Could not upsert to Pinecone: {str(e)}")
    
    @staticmethod
    def search_similar(query_text: str, top_k: int = 5, filter: dict = None) -> List[dict]:
        """Search for similar chunks in Pinecone"""
        try:
            print(f"[EMBEDDING] Generating embedding for query: {query_text[:50]}...")
            query_embedding = EmbeddingService.generate_embedding(query_text)
            print(f"[EMBEDDING] Query embedding size: {len(query_embedding)}")
            
            idx = EmbeddingService._get_index()
            if not idx:
                print(f"[EMBEDDING] ERROR: Index not available")
                return []
            
            print(f"[EMBEDDING] Querying Pinecone with top_k={top_k}, filter={filter}")
            results = idx.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            matches = results.get("matches", [])
            print(f"[EMBEDDING] Found {len(matches)} matches")
            
            for i, match in enumerate(matches[:3]):  # Log first 3 matches
                metadata = match.get("metadata", {})
                content = metadata.get("content", "")
                print(f"[EMBEDDING]   Match {i+1}: score={match.get('score'):.3f}, has_content={bool(content)}, content_length={len(content)}")
                if content:
                    print(f"[EMBEDDING]     Content preview: {content[:80]}...")
            
            return matches
        except Exception as e:
            print(f"[EMBEDDING] ERROR in search_similar: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def delete_chunk_embedding(chunk_id: str) -> None:
        """Delete a chunk embedding from Pinecone"""
        idx = EmbeddingService._get_index()
        if idx:
            try:
                idx.delete(ids=[chunk_id])
            except Exception as e:
                print(f"Warning: Could not delete from Pinecone: {str(e)}")
    
    @staticmethod
    def delete_document_embeddings(document_id: int) -> None:
        """Delete all embeddings for a document"""
        idx = EmbeddingService._get_index()
        if idx:
            try:
                idx.delete(filter={"document_id": {"$eq": document_id}})
            except Exception as e:
                print(f"Warning: Could not delete document embeddings: {str(e)}")


embedding_service = EmbeddingService()

