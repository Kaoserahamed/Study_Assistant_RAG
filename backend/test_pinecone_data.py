#!/usr/bin/env python3
"""
Test script to verify Pinecone index has data and embeddings are working
"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "student-assistant")

if not PINECONE_API_KEY:
    print("ERROR: PINECONE_API_KEY not found in environment")
    exit(1)

print(f"Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

try:
    # Get index info
    index_info = pc.describe_index(PINECONE_INDEX_NAME)
    print(f"\n✅ Index '{PINECONE_INDEX_NAME}' exists")
    print(f"   Dimension: {index_info.dimension}")
    print(f"   Metric: {index_info.metric}")
    print(f"   Host: {index_info.host}")
    
    # Connect to index
    index = pc.Index(PINECONE_INDEX_NAME)
    
    # Get index stats
    stats = index.describe_index_stats()
    print(f"\n📊 Index Statistics:")
    print(f"   Total vectors: {stats.get('total_vector_count', 0)}")
    print(f"   Namespaces: {stats.get('namespaces', {})}")
    
    if stats.get('total_vector_count', 0) == 0:
        print(f"\n⚠️  WARNING: Index is EMPTY! No vectors stored.")
        print(f"   You need to upload documents to populate the index.")
    else:
        print(f"\n✅ Index has data!")
        
        # Try a test query with a dummy vector
        print(f"\n🔍 Testing query with dummy vector...")
        dummy_vector = [0.1] * index_info.dimension
        results = index.query(
            vector=dummy_vector,
            top_k=5,
            include_metadata=True
        )
        
        print(f"   Query returned {len(results.get('matches', []))} results")
        
        if results.get('matches'):
            print(f"\n📄 Sample results:")
            for i, match in enumerate(results['matches'][:3]):
                metadata = match.get('metadata', {})
                print(f"\n   Result {i+1}:")
                print(f"      ID: {match.get('id')}")
                print(f"      Score: {match.get('score', 0):.4f}")
                print(f"      Document ID: {metadata.get('document_id')}")
                print(f"      User ID: {metadata.get('user_id')}")
                print(f"      Page: {metadata.get('page_number')}")
                print(f"      Content preview: {metadata.get('content', '')[:100]}...")
        
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
