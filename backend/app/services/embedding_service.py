# app/services/embedding_service.py
from typing import List
import os
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


class EmbeddingService:
    
    @staticmethod
    def _get_index():
        global index
        if index is None:
            _ensure_index_exists()
        return index
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generate embedding using Pinecone's inference API"""
        embedding_response = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[text],
            parameters={"input_type": "passage", "truncate": "END"}
        )
        return embedding_response.data[0].values
    
    @staticmethod
    def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """Generate multiple embeddings at once"""
        if not texts:
            return []
        
        embedding_response = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=texts,
            parameters={"input_type": "passage", "truncate": "END"}
        )
        return [embedding.values for embedding in embedding_response.data]
    
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
            query_embedding = EmbeddingService.generate_embedding(query_text)
            idx = EmbeddingService._get_index()
            if not idx:
                return []
            
            results = idx.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            return results.get("matches", [])
        except Exception as e:
            print(f"Warning: Search failed: {str(e)}")
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
