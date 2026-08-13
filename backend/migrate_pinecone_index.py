#!/usr/bin/env python3
"""
Migration script to recreate Pinecone index with correct dimension for Gemini embeddings

IMPORTANT: This will DELETE the existing index and all its data.
You will need to re-upload all documents after running this script.
"""
import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import time

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "student-assistant")
NEW_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))
METRIC = "cosine"

if not PINECONE_API_KEY:
    print("❌ ERROR: PINECONE_API_KEY not found in environment")
    sys.exit(1)

print("=" * 70)
print("PINECONE INDEX MIGRATION")
print("=" * 70)
print(f"\nThis script will:")
print(f"  1. Delete the existing index '{PINECONE_INDEX_NAME}' (dimension: 1024)")
print(f"  2. Create a new index '{PINECONE_INDEX_NAME}' (dimension: {NEW_DIMENSION})")
print(f"  3. You will need to re-upload all documents afterwards")
print(f"\n⚠️  WARNING: ALL EXISTING EMBEDDINGS WILL BE DELETED!")
print("=" * 70)

response = input(f"\nAre you sure you want to proceed? Type 'YES' to continue: ")

if response.strip().upper() != "YES":
    print("\n❌ Migration cancelled.")
    sys.exit(0)

print(f"\n🔧 Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)

try:
    # Check if index exists
    print(f"\n📋 Checking existing index...")
    try:
        index_info = pc.describe_index(PINECONE_INDEX_NAME)
        print(f"   ✅ Found index '{PINECONE_INDEX_NAME}'")
        print(f"      Current dimension: {index_info.dimension}")
        print(f"      Current metric: {index_info.metric}")
        
        # Get stats before deletion
        index = pc.Index(PINECONE_INDEX_NAME)
        stats = index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        print(f"      Total vectors: {total_vectors}")
        
        # Delete the index
        print(f"\n🗑️  Deleting existing index...")
        pc.delete_index(PINECONE_INDEX_NAME)
        print(f"   ✅ Index deleted successfully")
        
        # Wait for deletion to complete
        print(f"   ⏳ Waiting for deletion to complete...")
        time.sleep(5)
        
    except Exception as e:
        print(f"   ℹ️  Index does not exist or error checking: {str(e)}")
        print(f"   Will create new index...")
    
    # Create new index with correct dimension
    print(f"\n🏗️  Creating new index with dimension {NEW_DIMENSION}...")
    
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=NEW_DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    
    print(f"   ✅ Index creation initiated")
    
    # Wait for index to be ready
    print(f"   ⏳ Waiting for index to be ready...")
    max_wait = 60  # seconds
    waited = 0
    while waited < max_wait:
        try:
            index_info = pc.describe_index(PINECONE_INDEX_NAME)
            if index_info.status.get('ready', False):
                break
        except:
            pass
        time.sleep(2)
        waited += 2
        print(f"      Waiting... ({waited}s)")
    
    # Verify new index
    index_info = pc.describe_index(PINECONE_INDEX_NAME)
    print(f"\n✅ NEW INDEX CREATED SUCCESSFULLY!")
    print(f"   Name: {PINECONE_INDEX_NAME}")
    print(f"   Dimension: {index_info.dimension}")
    print(f"   Metric: {index_info.metric}")
    print(f"   Host: {index_info.host}")
    print(f"   Status: {'Ready' if index_info.status.get('ready') else 'Initializing'}")
    
    print(f"\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 70)
    print(f"\n📝 NEXT STEPS:")
    print(f"   1. Restart your FastAPI backend (it will connect to the new index)")
    print(f"   2. Re-upload all your documents through the web interface")
    print(f"   3. Documents will be processed with real Gemini embeddings")
    print(f"   4. Search will now work with semantic similarity")
    print(f"\n💡 TIP: The new embeddings will provide much better search results!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR during migration: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
