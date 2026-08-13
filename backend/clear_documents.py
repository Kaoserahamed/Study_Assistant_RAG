#!/usr/bin/env python3
"""
Script to clear all documents from the database and filesystem

This will:
1. Delete all document records from MySQL
2. Delete all chunk records
3. Delete all uploaded PDF files
4. Clear all embeddings from Pinecone (optional)
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import shutil

load_dotenv()

# Database connection
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "study_assistant")
DB_PORT = os.getenv("DB_PORT", "3306")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Pinecone config
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "student-assistant")

print("=" * 70)
print("CLEAR ALL DOCUMENTS")
print("=" * 70)
print("\nThis script will:")
print("  1. Delete all document records from MySQL database")
print("  2. Delete all chunk records")
print("  3. Delete all uploaded PDF files")
print("  4. Optionally clear Pinecone index")
print("\n⚠️  WARNING: THIS CANNOT BE UNDONE!")
print("=" * 70)

response = input("\nAre you sure you want to proceed? Type 'YES' to continue: ")

if response.strip().upper() != "YES":
    print("\n❌ Operation cancelled.")
    sys.exit(0)

try:
    # Connect to database
    print("\n🔧 Connecting to database...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check which tables exist
    print("\n🔍 Checking database tables...")
    tables_result = session.execute(text("SHOW TABLES"))
    existing_tables = [row[0] for row in tables_result]
    print(f"   Found tables: {existing_tables}")
    
    has_documents = 'documents' in existing_tables
    has_chunks = 'chunks' in existing_tables
    
    # Get counts before deletion
    print("\n📊 Current state:")
    doc_count = 0
    chunk_count = 0
    
    if has_documents:
        doc_count = session.execute(text("SELECT COUNT(*) FROM documents")).scalar()
        print(f"   Documents: {doc_count}")
    else:
        print(f"   Documents table: NOT FOUND")
    
    if has_chunks:
        chunk_count = session.execute(text("SELECT COUNT(*) FROM chunks")).scalar()
        print(f"   Chunks: {chunk_count}")
    else:
        print(f"   Chunks table: NOT FOUND")
    
    if doc_count == 0 and chunk_count == 0:
        print("\n✅ Database is already empty!")
    else:
        # Delete chunks first (foreign key constraint)
        if has_chunks and chunk_count > 0:
            print(f"\n🗑️  Deleting {chunk_count} chunks...")
            session.execute(text("DELETE FROM chunks"))
            session.commit()
            print("   ✅ Chunks deleted")
        
        # Delete documents
        if has_documents and doc_count > 0:
            print(f"\n🗑️  Deleting {doc_count} documents...")
            session.execute(text("DELETE FROM documents"))
            session.commit()
            print("   ✅ Documents deleted")
        
        # Reset auto-increment counters
        print("\n🔄 Resetting auto-increment counters...")
        if has_chunks:
            session.execute(text("ALTER TABLE chunks AUTO_INCREMENT = 1"))
        if has_documents:
            session.execute(text("ALTER TABLE documents AUTO_INCREMENT = 1"))
        session.commit()
        print("   ✅ Counters reset")
    
    session.close()
    
    # Delete uploaded files
    print("\n🗑️  Cleaning uploaded files directory...")
    uploaded_files_dir = os.path.join(os.path.dirname(__file__), "uploaded_files")
    
    if os.path.exists(uploaded_files_dir):
        file_count = len([f for f in os.listdir(uploaded_files_dir) if os.path.isfile(os.path.join(uploaded_files_dir, f))])
        
        if file_count > 0:
            for filename in os.listdir(uploaded_files_dir):
                file_path = os.path.join(uploaded_files_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"   ⚠️  Could not delete {filename}: {e}")
            
            remaining = len([f for f in os.listdir(uploaded_files_dir) if os.path.isfile(os.path.join(uploaded_files_dir, f))])
            print(f"   ✅ Deleted {file_count - remaining} files")
            if remaining > 0:
                print(f"   ⚠️  {remaining} files could not be deleted (may be in use)")
        else:
            print("   ℹ️  No files to delete")
    else:
        print("   ℹ️  uploaded_files directory does not exist")
    
    # Ask about Pinecone
    print("\n" + "=" * 70)
    clear_pinecone = input("\nDo you want to clear Pinecone index as well? Type 'YES' to clear: ")
    
    if clear_pinecone.strip().upper() == "YES":
        if not PINECONE_API_KEY:
            print("   ⚠️  PINECONE_API_KEY not found, skipping Pinecone cleanup")
        else:
            try:
                from pinecone import Pinecone
                
                print(f"\n🔧 Connecting to Pinecone...")
                pc = Pinecone(api_key=PINECONE_API_KEY)
                index = pc.Index(PINECONE_INDEX_NAME)
                
                # Get stats before deletion
                stats = index.describe_index_stats()
                vector_count = stats.get('total_vector_count', 0)
                print(f"   Current vectors: {vector_count}")
                
                if vector_count > 0:
                    print(f"\n🗑️  Deleting all vectors from Pinecone index...")
                    # Delete all vectors by deleting with empty filter (deletes everything)
                    index.delete(delete_all=True)
                    print("   ✅ Pinecone index cleared")
                else:
                    print("   ℹ️  Pinecone index is already empty")
                    
            except Exception as e:
                print(f"   ❌ Error clearing Pinecone: {str(e)}")
    else:
        print("   ℹ️  Skipping Pinecone cleanup")
    
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 70)
    print("\n📝 Summary:")
    print(f"   - Database documents: CLEARED")
    print(f"   - Database chunks: CLEARED")
    print(f"   - Uploaded files: CLEARED")
    print(f"   - Pinecone index: {'CLEARED' if clear_pinecone.strip().upper() == 'YES' else 'NOT CLEARED'}")
    print("\n💡 You can now upload fresh documents with the new embeddings!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
