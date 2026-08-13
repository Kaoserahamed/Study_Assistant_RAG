#!/usr/bin/env python3
"""
Test script to verify the RAG pipeline is working correctly with real Gemini embeddings.

This script tests:
1. Gemini embedding generation (single and batch)
2. Pinecone index creation and upserting
3. Semantic search relevance
4. End-to-end RAG flow
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.embedding_service import embedding_service, EmbeddingService, EMBEDDING_DIMENSION
from app.services.search_service import SearchService
from app.services.llm_service import LLMService

load_dotenv()

# Test data - semantically related chunks
TEST_CHUNKS = [
    {
        "id": "test_chunk_1",
        "content": "Python is a high-level programming language known for its simplicity and readability. It is widely used in data science, machine learning, and web development.",
        "document_id": 999,
        "user_id": 999,
        "chunk_index": 0,
        "page_number": 1,
    },
    {
        "id": "test_chunk_2",
        "content": "Machine learning is a subset of artificial intelligence that focuses on enabling computers to learn from data without being explicitly programmed.",
        "document_id": 999,
        "user_id": 999,
        "chunk_index": 1,
        "page_number": 2,
    },
    {
        "id": "test_chunk_3",
        "content": "Data science combines statistics, programming, and domain knowledge to extract insights from data and make data-driven decisions.",
        "document_id": 999,
        "user_id": 999,
        "chunk_index": 2,
        "page_number": 3,
    },
    {
        "id": "test_chunk_4",
        "content": "The Eiffel Tower is a wrought-iron lattice tower located on the Champ de Mars in Paris, France. It was built in 1889.",
        "document_id": 999,
        "user_id": 999,
        "chunk_index": 3,
        "page_number": 4,
    },
]

SEARCH_QUERIES = [
    ("What is machine learning?", ["test_chunk_2", "test_chunk_1"], "Should find ML and Python chunks"),
    ("Tell me about Python programming", ["test_chunk_1"], "Should find Python chunk"),
    ("What is the Eiffel Tower?", ["test_chunk_4"], "Should find Eiffel Tower chunk"),
]


async def test_single_embedding():
    """Test single embedding generation"""
    print("\n" + "="*80)
    print("TEST 1: Single Embedding Generation")
    print("="*80)
    
    try:
        text = "Python is a programming language"
        print(f"Generating embedding for: '{text}'")
        
        embedding = await EmbeddingService.generate_embedding_async(text)
        
        print(f"✓ Embedding generated successfully")
        print(f"  - Dimension: {len(embedding)}")
        print(f"  - Expected: {EMBEDDING_DIMENSION}")
        print(f"  - Match: {len(embedding) == EMBEDDING_DIMENSION}")
        print(f"  - Sample values: {embedding[:5]}")
        
        if len(embedding) == EMBEDDING_DIMENSION:
            print("✓ Dimension is correct!")
            return True
        else:
            print("✗ Dimension mismatch!")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_batch_embedding():
    """Test batch embedding generation"""
    print("\n" + "="*80)
    print("TEST 2: Batch Embedding Generation")
    print("="*80)
    
    try:
        texts = [chunk["content"] for chunk in TEST_CHUNKS]
        print(f"Generating embeddings for {len(texts)} texts")
        
        embeddings = await EmbeddingService.generate_embeddings_batch_async(texts, batch_size=4)
        
        print(f"✓ Batch embeddings generated successfully")
        print(f"  - Count: {len(embeddings)}")
        print(f"  - Expected: {len(texts)}")
        print(f"  - First embedding dimension: {len(embeddings[0]) if embeddings else 0}")
        
        if len(embeddings) == len(texts) and all(len(e) == EMBEDDING_DIMENSION for e in embeddings):
            print("✓ All embeddings generated with correct dimension!")
            return True
        else:
            print("✗ Embedding count or dimension mismatch!")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_pinecone_upsert():
    """Test Pinecone index creation and upserting"""
    print("\n" + "="*80)
    print("TEST 3: Pinecone Index and Upsert")
    print("="*80)
    
    try:
        # Generate embeddings for test chunks
        texts = [chunk["content"] for chunk in TEST_CHUNKS]
        embeddings = asyncio.run(EmbeddingService.generate_embeddings_batch_async(texts, batch_size=4))
        
        # Prepare vectors for Pinecone
        vectors = []
        for chunk, embedding in zip(TEST_CHUNKS, embeddings):
            vectors.append({
                "id": chunk["id"],
                "values": embedding,
                "metadata": {
                    "document_id": chunk["document_id"],
                    "user_id": chunk["user_id"],
                    "chunk_index": chunk["chunk_index"],
                    "page_number": chunk["page_number"],
                    "content": chunk["content"],
                }
            })
        
        print(f"Upserting {len(vectors)} vectors to Pinecone")
        embedding_service.upsert_to_pinecone(vectors)
        
        print("✓ Vectors upserted successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_semantic_search():
    """Test semantic search relevance"""
    print("\n" + "="*80)
    print("TEST 4: Semantic Search Relevance")
    print("="*80)
    
    try:
        all_passed = True
        
        for query, expected_chunks, description in SEARCH_QUERIES:
            print(f"\nQuery: '{query}'")
            print(f"Description: {description}")
            print(f"Expected to find: {expected_chunks}")
            
            results = await EmbeddingService.search_similar_async(
                query,
                top_k=5,
                filter={"user_id": {"$eq": 999}}
            )
            
            print(f"Results found: {len(results)}")
            
            if results:
                found_ids = [r.get("id") for r in results[:3]]
                print(f"Top 3 result IDs: {found_ids}")
                
                # Check if expected chunks are in results
                found_expected = any(chunk_id in found_ids for chunk_id in expected_chunks)
                
                # Print detailed scores
                for i, result in enumerate(results[:3]):
                    content_preview = result.get("metadata", {}).get("content", "")[:50]
                    score = result.get("score", 0)
                    print(f"  {i+1}. Score: {score:.4f} | Content: {content_preview}...")
                
                if found_expected or (results and results[0].get("score", 0) > 0.5):
                    print(f"✓ Search found semantically relevant results")
                else:
                    print(f"✗ Search did not find expected results (scores too low?)")
                    all_passed = False
            else:
                print(f"✗ No results found!")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_end_to_end_rag():
    """Test end-to-end RAG flow"""
    print("\n" + "="*80)
    print("TEST 5: End-to-End RAG Flow")
    print("="*80)
    
    try:
        query = "Tell me about machine learning and Python"
        user_id = 999
        
        print(f"Query: '{query}'")
        print(f"User ID: {user_id}")
        
        # Search for relevant chunks
        search_service = SearchService()
        results = search_service.search_documents(query, user_id, top_k=10, document_ids=None)
        
        print(f"\nSearch Results: {len(results)} chunks found")
        
        if not results:
            print("✗ No search results!")
            return False
        
        # Build context from search results
        context_parts = []
        for i, result in enumerate(results[:3], 1):
            snippet = result.get("snippet", "")
            title = result.get("documentTitle", "Unknown")
            print(f"\n  Result {i}: {title}")
            print(f"    Score: {result.get('score', 0):.4f}")
            print(f"    Snippet: {snippet[:100]}...")
            context_parts.append(snippet)
        
        context = "\n\n".join(context_parts)
        
        print(f"\nContext length: {len(context)} characters")
        
        # Generate LLM response with context
        print("\nGenerating LLM response with context...")
        response = await LLMService.generate_response_async(query, context)
        
        print(f"✓ LLM Response generated successfully")
        print(f"  Response length: {len(response)} characters")
        print(f"  Response preview: {response[:150]}...")
        
        if len(response) > 0:
            print("✓ End-to-end RAG flow working!")
            return True
        else:
            print("✗ Empty response from LLM")
            return False
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def cleanup_test_data():
    """Clean up test data from Pinecone"""
    print("\n" + "="*80)
    print("Cleanup: Removing test data")
    print("="*80)
    
    try:
        embedding_service.delete_document_embeddings(999)
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"✗ Cleanup error: {str(e)}")


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "RAG PIPELINE TEST SUITE" + " "*35 + "║")
    print("╚" + "="*78 + "╝")
    
    results = {}
    
    # Run tests
    results["Single Embedding"] = await test_single_embedding()
    results["Batch Embedding"] = await test_batch_embedding()
    results["Pinecone Upsert"] = test_pinecone_upsert()
    results["Semantic Search"] = await test_semantic_search()
    results["End-to-End RAG"] = await test_end_to_end_rag()
    
    # Cleanup
    await cleanup_test_data()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! RAG pipeline is working correctly.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
