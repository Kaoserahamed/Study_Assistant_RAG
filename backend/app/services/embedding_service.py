# app/services/embedding_service.py
from typing import List
import os
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
import logging
import httpx
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "student-assistant")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY environment variable not set")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = None

# Gemini supports a configurable output dimension. It must exactly match the
# Pinecone index dimension; set EMBEDDING_DIMENSION in .env for an existing index.
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
EMBEDDING_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


async def _generate_embedding_async(text: str) -> List[float]:
    """Generate embedding for a single text using Google's Gemini embedding API (async)
    
    Args:
        text: Input text to embed
        
    Returns:
        768-dimensional embedding vector
    """
    if not text or len(text.strip()) == 0:
        return [0.0] * EMBEDDING_DIMENSION
    
    try:
        url = f"{EMBEDDING_API_BASE}/{GEMINI_EMBEDDING_MODEL}:embedContent"
        
        payload = {
            "model": f"models/{GEMINI_EMBEDDING_MODEL}",
            "content": {
                "parts": [{"text": text}]
            },
            "taskType": "RETRIEVAL_QUERY",
            "outputDimensionality": EMBEDDING_DIMENSION,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers={"x-goog-api-key": GEMINI_API_KEY})
        
        if response.status_code != 200:
            error_text = response.text[:300]
            print(f"[EMBEDDING] ERROR: Gemini API error {response.status_code}: {error_text}")
            raise Exception(f"Gemini embedding API error: {response.status_code}")
        
        result = response.json()
        
        if "embedding" in result and "values" in result["embedding"]:
            embedding = result["embedding"]["values"]
            if len(embedding) != EMBEDDING_DIMENSION:
                print(f"[EMBEDDING] WARNING: Expected dimension {EMBEDDING_DIMENSION}, got {len(embedding)}")
            return embedding
        else:
            print(f"[EMBEDDING] ERROR: Unexpected Gemini API response structure: {result}")
            raise Exception("Unexpected Gemini embedding response")
            
    except Exception as e:
        print(f"[EMBEDDING] ERROR in _generate_embedding_async: {str(e)}")
        raise


async def _generate_embeddings_batch_async(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts in a single batch API call (async)
    
    This is much faster than calling per-text since we batch into one API request.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    # Filter empty texts
    non_empty_texts = [t if t and len(t.strip()) > 0 else "" for t in texts]
    
    if not any(non_empty_texts):
        return [[0.0] * EMBEDDING_DIMENSION for _ in texts]
    
    try:
        print(f"[EMBEDDING] Batch embedding {len(texts)} texts via Gemini API...")
        url = f"{EMBEDDING_API_BASE}/{GEMINI_EMBEDDING_MODEL}:batchEmbedContents"
        
        # Build batch request with all texts
        # Each request must specify the model
        batch_requests = []
        for text in non_empty_texts:
            batch_requests.append({
                "model": f"models/{GEMINI_EMBEDDING_MODEL}",  # Model must be specified with "models/" prefix
                "content": {
                    "parts": [{"text": text}]
                },
                "taskType": "RETRIEVAL_DOCUMENT",
                "outputDimensionality": EMBEDDING_DIMENSION,
            })
        
        payload = {
            "requests": batch_requests
        }
        
        start_time = time.time()
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers={"x-goog-api-key": GEMINI_API_KEY})
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            error_text = response.text[:500]
            print(f"[EMBEDDING] ERROR: Gemini batch API error {response.status_code}: {error_text}")
            raise Exception(f"Gemini batch embedding API error: {response.status_code}")
        
        result = response.json()
        
        embeddings = []
        if "embeddings" in result:
            for emb_data in result["embeddings"]:
                if "values" in emb_data:
                    embeddings.append(emb_data["values"])
                else:
                    print(f"[EMBEDDING] WARNING: Missing embedding in response, using zero vector")
                    embeddings.append([0.0] * EMBEDDING_DIMENSION)
        
        if len(embeddings) != len(texts):
            raise ValueError(f"Gemini returned {len(embeddings)} embeddings for {len(texts)} chunks")
        if any(len(embedding) != EMBEDDING_DIMENSION for embedding in embeddings):
            raise ValueError(f"Gemini returned an embedding with an unexpected dimension; expected {EMBEDDING_DIMENSION}")
        print(f"[EMBEDDING] Batch API call took {elapsed:.2f}s for {len(embeddings)} embeddings")
        return embeddings
        
    except Exception as e:
        print(f"[EMBEDDING] ERROR in _generate_embeddings_batch_async: {str(e)}")
        raise


def _ensure_index_exists():
    """Ensure Pinecone index exists with correct dimensions and settings"""
    global index
    try:
        # Try to describe existing index
        index_info = pc.describe_index(PINECONE_INDEX_NAME)
        print(f"[EMBEDDING] Index '{PINECONE_INDEX_NAME}' exists with dimension: {index_info.dimension}")
        
        # Verify dimension matches our embedding model
        if index_info.dimension != EMBEDDING_DIMENSION:
            raise RuntimeError(
                f"Pinecone index dimension is {index_info.dimension}; expected {EMBEDDING_DIMENSION}. "
                "Recreate the index and re-upload all documents before using RAG."
            )
            # Kept below for old log context; the exception above prevents a partial upload.
            print(f"[EMBEDDING] ❌ CRITICAL ERROR: Index dimension mismatch!")
            print(f"[EMBEDDING]    Expected: {EMBEDDING_DIMENSION} (Gemini text-embedding-004)")
            print(f"[EMBEDDING]    Actual:   {index_info.dimension} (old fake embeddings)")
            print(f"[EMBEDDING]")
            print(f"[EMBEDDING] 🔧 SOLUTION:")
            print(f"[EMBEDDING]    1. Run: python backend/migrate_pinecone_index.py")
            print(f"[EMBEDDING]    2. Re-upload all documents")
            print(f"[EMBEDDING]")
            print(f"[EMBEDDING] ⚠️  Search will NOT work until index is migrated!")
            # Still connect to allow other operations, but search will fail
        
        index = pc.Index(PINECONE_INDEX_NAME)
        print(f"[EMBEDDING] Successfully connected to index")
        
    except RuntimeError:
        # A dimension mismatch is a configuration error, not a missing index.
        raise
    except Exception as e:
        print(f"[EMBEDDING] Index does not exist or error accessing it: {str(e)}")
        print(f"[EMBEDDING] Attempting to create index '{PINECONE_INDEX_NAME}' with dimension {EMBEDDING_DIMENSION}...")
        
        try:
            # Create new index with correct dimension - THIS ACTUALLY CREATES IT
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",  # Use cosine similarity for semantic search
                spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
            )
            print(f"[EMBEDDING] ✅ Index created successfully")
            # Now connect to it
            index = pc.Index(PINECONE_INDEX_NAME)
            print(f"[EMBEDDING] Successfully connected to newly created index")
            
        except Exception as create_error:
            print(f"[EMBEDDING] CRITICAL ERROR: Could not create index: {str(create_error)}")
            print(f"[EMBEDDING] Please create the index manually in Pinecone with:")
            print(f"[EMBEDDING]   - Name: {PINECONE_INDEX_NAME}")
            print(f"[EMBEDDING]   - Dimension: {EMBEDDING_DIMENSION}")
            print(f"[EMBEDDING]   - Metric: cosine")
            # Continue anyway - will fail on upsert
            index = None


class EmbeddingService:
    """Service for generating embeddings and managing vector search"""
    
    @staticmethod
    def _get_index():
        """Get Pinecone index, initializing if needed"""
        global index
        if index is None:
            _ensure_index_exists()
        return index
    
    @staticmethod
    async def generate_embedding_async(text: str) -> List[float]:
        """Generate embedding for a single text using Gemini API (async)
        
        Args:
            text: Input text to embed
            
        Returns:
            768-dimensional embedding vector
        """
        return await _generate_embedding_async(text)
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generate embedding for a single text (sync wrapper)
        
        This is a blocking wrapper around the async version.
        For use in sync contexts only.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context, should use generate_embedding_async instead
                print("[EMBEDDING] WARNING: Called sync generate_embedding from async context")
                # Run in thread to avoid blocking
                return loop.run_in_executor(None, lambda: asyncio.run(_generate_embedding_async(text)))
            return loop.run_until_complete(_generate_embedding_async(text))
        except RuntimeError:
            # No event loop - create one
            return asyncio.run(_generate_embedding_async(text))
    
    @staticmethod
    async def generate_embeddings_batch_async(texts: List[str], batch_size: int = 128) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently (async)
        
        Batches requests to the Gemini embedding API.
        
        Args:
            texts: List of texts to embed
            batch_size: Size of each batch (Gemini supports up to 128 per request)
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        print(f"[EMBEDDING] Generating embeddings for {len(texts)} texts in batches of {batch_size}")
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            print(f"[EMBEDDING] Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            batch_embeddings = await _generate_embeddings_batch_async(batch_texts)
            all_embeddings.extend(batch_embeddings)
        
        print(f"[EMBEDDING] Generated {len(all_embeddings)} embeddings total")
        return all_embeddings
    
    @staticmethod
    def generate_embeddings_batch(texts: List[str], batch_size: int = 128) -> List[List[float]]:
        """Generate embeddings for multiple texts (sync wrapper)
        
        This is a blocking wrapper around the async version.
        For use in sync contexts only.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context, should use generate_embeddings_batch_async instead
                print("[EMBEDDING] WARNING: Called sync generate_embeddings_batch from async context")
                # Run in thread to avoid blocking
                return loop.run_in_executor(None, lambda: asyncio.run(_generate_embeddings_batch_async(texts, batch_size)))
            return loop.run_until_complete(_generate_embeddings_batch_async(texts, batch_size))
        except RuntimeError:
            # No event loop - create one
            return asyncio.run(_generate_embeddings_batch_async(texts, batch_size))
    
    @staticmethod
    async def upsert_to_pinecone_async(vectors: List[dict]) -> None:
        """Store vectors in Pinecone index (async, non-blocking)
        
        Args:
            vectors: List of dicts with format:
                {
                    "id": "unique_id",
                    "values": [0.1, 0.2, ...],  # Must be EMBEDDING_DIMENSION size
                    "metadata": {
                        "document_id": 1,
                        "chunk_index": 0,
                        "content": "...",
                        "page_number": 1,
                        ...
                    }
                }
        """
        if not vectors:
            return
        
        idx = EmbeddingService._get_index()
        if not idx:
            raise RuntimeError("Pinecone index is not available; document was not indexed.")
        
        try:
            # Verify vector dimensions
            if vectors and len(vectors[0].get("values", [])) != EMBEDDING_DIMENSION:
                actual_dim = len(vectors[0].get("values", []))
                raise ValueError(f"Vector dimension mismatch: expected {EMBEDDING_DIMENSION}, got {actual_dim}")
            
            print(f"[EMBEDDING] Upserting {len(vectors)} vectors to Pinecone (async)")
            # Run blocking Pinecone call in thread pool to avoid blocking event loop
            await asyncio.to_thread(idx.upsert, vectors=vectors)
            print(f"[EMBEDDING] Upsert successful")
            
        except Exception as e:
            print(f"[EMBEDDING] ERROR: Could not upsert to Pinecone: {str(e)}")
            raise RuntimeError(f"Could not index document chunks: {e}") from e
    
    @staticmethod
    def upsert_to_pinecone(vectors: List[dict]) -> None:
        """Store vectors in Pinecone index (sync wrapper)
        
        For use in sync contexts only.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                print("[EMBEDDING] WARNING: Called sync upsert_to_pinecone from async context")
                return
            loop.run_until_complete(EmbeddingService.upsert_to_pinecone_async(vectors))
        except RuntimeError:
            asyncio.run(EmbeddingService.upsert_to_pinecone_async(vectors))
    
    @staticmethod
    async def search_similar_async(query_text: str, top_k: int = 10, filter: dict = None) -> List[dict]:
        """Search for semantically similar chunks in Pinecone (async)
        
        Args:
            query_text: User query to search for
            top_k: Number of top results to return
            filter: Pinecone metadata filter (e.g., {"user_id": {"$eq": 123}})
            
        Returns:
            List of matches with metadata and similarity scores
        """
        try:
            if not query_text or len(query_text.strip()) == 0:
                print(f"[EMBEDDING] ERROR: Empty query text")
                return []
            
            print(f"[EMBEDDING] Generating embedding for query: {query_text[:60]}...")
            query_embedding = await _generate_embedding_async(query_text)
            print(f"[EMBEDDING] Query embedding dimension: {len(query_embedding)}")
            
            idx = EmbeddingService._get_index()
            if not idx:
                print(f"[EMBEDDING] ERROR: Pinecone index not available")
                return []
            
            print(f"[EMBEDDING] Querying Pinecone with top_k={top_k}, filter={'present' if filter else 'none'}")
            # Run blocking Pinecone query in thread pool to avoid blocking event loop
            results = await asyncio.to_thread(
                idx.query,
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter
            )
            
            matches = results.get("matches", [])
            print(f"[EMBEDDING] Found {len(matches)} semantic matches")
            
            # Log top matches for debugging
            for i, match in enumerate(matches[:3]):
                metadata = match.get("metadata", {})
                score = match.get("score", 0)
                content_len = len(metadata.get("content", ""))
                print(f"[EMBEDDING]   Match {i+1}: score={score:.4f}, content_len={content_len}, chunk_idx={metadata.get('chunk_index')}")
            
            return matches
            
        except Exception as e:
            print(f"[EMBEDDING] ERROR in search_similar_async: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def search_similar(query_text: str, top_k: int = 10, filter: dict = None) -> List[dict]:
        """Search for semantically similar chunks in Pinecone (sync wrapper)
        
        This is a blocking wrapper around the async version.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context, should use search_similar_async instead
                print("[EMBEDDING] WARNING: Called sync search_similar from async context")
                # Run in thread to avoid blocking
                return loop.run_in_executor(None, lambda: asyncio.run(_search_similar_internal(query_text, top_k, filter)))
            return loop.run_until_complete(_search_similar_internal(query_text, top_k, filter))
        except RuntimeError:
            # No event loop - create one
            return asyncio.run(_search_similar_internal(query_text, top_k, filter))
    
    @staticmethod
    async def delete_chunk_embedding_async(chunk_id: str) -> None:
        """Delete a single chunk embedding from Pinecone (async)"""
        idx = EmbeddingService._get_index()
        if idx:
            try:
                await asyncio.to_thread(idx.delete, ids=[chunk_id])
            except Exception as e:
                print(f"[EMBEDDING] WARNING: Could not delete chunk: {str(e)}")
    
    @staticmethod
    def delete_chunk_embedding(chunk_id: str) -> None:
        """Delete a single chunk embedding from Pinecone (sync wrapper)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return
            loop.run_until_complete(EmbeddingService.delete_chunk_embedding_async(chunk_id))
        except RuntimeError:
            asyncio.run(EmbeddingService.delete_chunk_embedding_async(chunk_id))
    
    @staticmethod
    async def delete_document_embeddings_async(document_id: int) -> None:
        """Delete all embeddings for a document (async)"""
        idx = EmbeddingService._get_index()
        if idx:
            try:
                await asyncio.to_thread(idx.delete, filter={"document_id": {"$eq": document_id}})
            except Exception as e:
                print(f"[EMBEDDING] WARNING: Could not delete document embeddings: {str(e)}")
    
    @staticmethod
    def delete_document_embeddings(document_id: int) -> None:
        """Delete all embeddings for a document (sync wrapper)"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return
            loop.run_until_complete(EmbeddingService.delete_document_embeddings_async(document_id))
        except RuntimeError:
            asyncio.run(EmbeddingService.delete_document_embeddings_async(document_id))


async def _search_similar_internal(query_text: str, top_k: int, filter: dict) -> List[dict]:
    """Internal async search implementation"""
    return await EmbeddingService.search_similar_async(query_text, top_k, filter)


embedding_service = EmbeddingService()
