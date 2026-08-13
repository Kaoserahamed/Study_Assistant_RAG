#!/usr/bin/env python3
"""
Script to drop and recreate the entire database with fresh tables

This will:
1. Drop the entire database
2. Create a new empty database
3. Create all tables with correct schema
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# Database connection
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "study_assistant")
DB_PORT = os.getenv("DB_PORT", "3306")

print("=" * 70)
print("RECREATE DATABASE")
print("=" * 70)
print(f"\nThis script will:")
print(f"  1. Drop database '{DB_NAME}'")
print(f"  2. Create new empty database '{DB_NAME}'")
print(f"  3. Create all tables with correct schema")
print(f"\n⚠️  WARNING: ALL DATA WILL BE LOST!")
print("=" * 70)

response = input("\nAre you sure you want to proceed? Type 'YES' to continue: ")

if response.strip().upper() != "YES":
    print("\n❌ Operation cancelled.")
    sys.exit(0)

try:
    # Connect to MySQL server (not to specific database)
    print("\n🔧 Connecting to MySQL server...")
    server_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    engine = create_engine(server_url)
    
    with engine.connect() as conn:
        # Drop database
        print(f"\n🗑️  Dropping database '{DB_NAME}'...")
        conn.execute(text(f"DROP DATABASE IF EXISTS `{DB_NAME}`"))
        conn.commit()
        print(f"   ✅ Database dropped")
        
        # Create database
        print(f"\n🏗️  Creating database '{DB_NAME}'...")
        conn.execute(text(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
        print(f"   ✅ Database created")
    
    # Now connect to the new database and create tables
    print(f"\n🏗️  Creating tables...")
    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_email (email)
            )
        """))
        print(f"   ✅ Created table: users")
        
        # Create documents table
        conn.execute(text("""
            CREATE TABLE documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                page_count INT DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            )
        """))
        print(f"   ✅ Created table: documents")
        
        # Create chunks table
        conn.execute(text("""
            CREATE TABLE chunks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                document_id INT NOT NULL,
                chunk_index INT NOT NULL,
                content TEXT NOT NULL,
                page_number INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                INDEX idx_document_id (document_id),
                INDEX idx_chunk_index (chunk_index)
            )
        """))
        print(f"   ✅ Created table: chunks")
        
        # Create conversations table
        conn.execute(text("""
            CREATE TABLE conversations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) DEFAULT 'New Conversation',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            )
        """))
        print(f"   ✅ Created table: conversations")
        
        # Create messages table
        conn.execute(text("""
            CREATE TABLE messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversation_id INT NOT NULL,
                role ENUM('user', 'assistant') NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                INDEX idx_conversation_id (conversation_id)
            )
        """))
        print(f"   ✅ Created table: messages")
        
        conn.commit()
    
    print("\n" + "=" * 70)
    print("✅ DATABASE RECREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📝 Summary:")
    print(f"   - Database '{DB_NAME}': CREATED")
    print(f"   - Tables created: users, documents, chunks, conversations, messages")
    print(f"   - All data: CLEARED")
    print("\n💡 Next steps:")
    print(f"   1. Start your backend: python main.py")
    print(f"   2. Register a new user through the frontend")
    print(f"   3. Upload documents with new embeddings!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
