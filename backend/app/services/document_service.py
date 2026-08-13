# app/services/document_service.py
from typing import List
import asyncio
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import time
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository
from app.services.pdf_service import PDFService
from app.services.embedding_service import embedding_service
from app.models.document import Document

class DocumentService:
    def __init__(self, db: Session):
        self.doc_repo = DocumentRepository(db)
        self.chunk_repo = ChunkRepository(db)

    async def process_and_save_document_async(self, file: UploadFile, user_id: int) -> Document:
        """Process and save document with async embedding generation"""
        print(f"\n[DOCUMENT] === PROCESSING DOCUMENT (ASYNC) ===")
        print(f"[DOCUMENT] File: {file.filename}")
        print(f"[DOCUMENT] User: {user_id}")
        
        # Validate file size (50MB limit)
        MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
        
        # Read file content to check size
        content = await file.read()
        file_size = len(content)
        
        print(f"[DOCUMENT] File size: {file_size / (1024 * 1024):.2f} MB")
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Reset file pointer for processing
        await file.seek(0)
        
        # PDF parsing and file I/O are CPU/blocking work.  Keep them off the
        # FastAPI event loop so one large upload cannot stall chat responses.
        file_path = await asyncio.to_thread(PDFService.save_file, file)
        print(f"[DOCUMENT] Saved to: {file_path}")

        doc = None
        try:
            print(f"[DOCUMENT] Extracting chunks...")
            extract_start = time.time()
            page_count, chunks_data = await asyncio.to_thread(PDFService.extract_chunks, file_path)
            extract_time = time.time() - extract_start
            
            print(f"[DOCUMENT] Extracted {len(chunks_data)} chunks from {page_count} pages in {extract_time:.2f}s")
            
            if not chunks_data:
                print(f"[DOCUMENT] ERROR: No chunks extracted!")
                raise ValueError(
                    "No selectable text was found. This is usually a scanned/image-only PDF; "
                    "run OCR on it or upload a text-based PDF."
                )
            
            # Show first chunk
            if chunks_data:
                print(f"[DOCUMENT] First chunk (page {chunks_data[0]['page_number']}, index {chunks_data[0]['chunk_index']}): {chunks_data[0]['content'][:100]}...")

            print(f"[DOCUMENT] Creating database record...")
            doc = self.doc_repo.create(
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                page_count=page_count
            )
            print(f"[DOCUMENT] Document created with ID: {doc.id}")

            # Process chunks in batches to avoid memory issues
            BATCH_SIZE = 100  # Larger batches for faster processing
            print(f"[DOCUMENT] Processing {len(chunks_data)} chunks in batches of {BATCH_SIZE}...")
            
            # Save chunks to database first
            print(f"[DOCUMENT] Saving chunks to database...")
            self.chunk_repo.bulk_create(document_id=doc.id, chunks_data=chunks_data)
            print(f"[DOCUMENT] Chunks saved to database")
            
            # Process embeddings and Pinecone in batches (ASYNC)
            total_chunks = len(chunks_data)
            for batch_start in range(0, total_chunks, BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, total_chunks)
                batch_chunks = chunks_data[batch_start:batch_end]
                
                batch_num = batch_start // BATCH_SIZE + 1
                total_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE
                print(f"[DOCUMENT] Processing batch {batch_num}/{total_batches} (chunks {batch_start+1}-{batch_end})...")
                
                # Generate embeddings for batch (ASYNC)
                embed_start = time.time()
                chunk_texts = [chunk["content"] for chunk in batch_chunks]
                embeddings = await embedding_service.generate_embeddings_batch_async(chunk_texts)
                embed_time = time.time() - embed_start
                
                print(f"[DOCUMENT] Generated {len(embeddings)} embeddings in {embed_time:.2f}s")
                
                # Prepare vectors for Pinecone - ensure metadata is complete
                pinecone_vectors = []
                for chunk, embedding in zip(batch_chunks, embeddings):
                    vector_id = f"doc_{doc.id}_chunk_{chunk['chunk_index']}"
                    
                    # Ensure content is included in metadata
                    pinecone_vectors.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {
                            "document_id": doc.id,
                            "user_id": user_id,
                            "chunk_index": chunk["chunk_index"],
                            "page_number": chunk["page_number"],
                            "content": chunk["content"]  # IMPORTANT: Include actual content
                        }
                    })
                
                # Upsert batch to Pinecone (ASYNC)
                pinecone_start = time.time()
                print(f"[DOCUMENT] Upserting {len(pinecone_vectors)} vectors to Pinecone (async)...")
                await embedding_service.upsert_to_pinecone_async(pinecone_vectors)
                pinecone_time = time.time() - pinecone_start
                print(f"[DOCUMENT] Batch {batch_num} upserted in {pinecone_time:.2f}s")
                
                # Clear batch data from memory
                del chunk_texts, embeddings, pinecone_vectors
            
            print(f"[DOCUMENT] All {total_batches} batches processed successfully")
            
            print(f"[DOCUMENT] === PROCESSING COMPLETE ===\n")
            return doc

        except Exception as e:
            print(f"[DOCUMENT] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            if doc:
                # Earlier batches may already be searchable; remove them before
                # deleting the SQL record so failed uploads cannot pollute RAG.
                try:
                    await embedding_service.delete_document_embeddings_async(doc.id)
                except Exception as cleanup_error:
                    print(f"[DOCUMENT] WARNING: Could not remove partial embeddings: {cleanup_error}")
                finally:
                    self.doc_repo.delete(doc)
            await asyncio.to_thread(PDFService.delete_file, file_path)
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    def process_and_save_document(self, file: UploadFile, user_id: int) -> Document:
        print(f"\n[DOCUMENT] === PROCESSING DOCUMENT ===")
        print(f"[DOCUMENT] File: {file.filename}")
        print(f"[DOCUMENT] User: {user_id}")
        
        file_path = PDFService.save_file(file)
        print(f"[DOCUMENT] Saved to: {file_path}")

        doc = None
        try:
            print(f"[DOCUMENT] Extracting chunks...")
            extract_start = time.time()
            page_count, chunks_data = PDFService.extract_chunks(file_path)
            extract_time = time.time() - extract_start
            
            print(f"[DOCUMENT] Extracted {len(chunks_data)} chunks from {page_count} pages in {extract_time:.2f}s")
            
            if not chunks_data:
                print(f"[DOCUMENT] ERROR: No chunks extracted!")
                raise ValueError(
                    "No selectable text was found. This is usually a scanned/image-only PDF; "
                    "run OCR on it or upload a text-based PDF."
                )
            
            # Show first chunk
            if chunks_data:
                print(f"[DOCUMENT] First chunk (page {chunks_data[0]['page_number']}, index {chunks_data[0]['chunk_index']}): {chunks_data[0]['content'][:100]}...")

            print(f"[DOCUMENT] Creating database record...")
            doc = self.doc_repo.create(
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                page_count=page_count
            )
            print(f"[DOCUMENT] Document created with ID: {doc.id}")

            # Process chunks in batches to avoid memory issues
            BATCH_SIZE = 100  # Larger batches for faster processing
            print(f"[DOCUMENT] Processing {len(chunks_data)} chunks in batches of {BATCH_SIZE}...")
            
            # Save chunks to database first
            print(f"[DOCUMENT] Saving chunks to database...")
            self.chunk_repo.bulk_create(document_id=doc.id, chunks_data=chunks_data)
            print(f"[DOCUMENT] Chunks saved to database")
            
            # Process embeddings and Pinecone in batches
            total_chunks = len(chunks_data)
            for batch_start in range(0, total_chunks, BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, total_chunks)
                batch_chunks = chunks_data[batch_start:batch_end]
                
                batch_num = batch_start // BATCH_SIZE + 1
                total_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE
                print(f"[DOCUMENT] Processing batch {batch_num}/{total_batches} (chunks {batch_start+1}-{batch_end})...")
                
                # Generate embeddings for batch
                embed_start = time.time()
                chunk_texts = [chunk["content"] for chunk in batch_chunks]
                embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
                embed_time = time.time() - embed_start
                
                print(f"[DOCUMENT] Generated {len(embeddings)} embeddings in {embed_time:.2f}s")
                
                # Prepare vectors for Pinecone - ensure metadata is complete
                pinecone_vectors = []
                for chunk, embedding in zip(batch_chunks, embeddings):
                    vector_id = f"doc_{doc.id}_chunk_{chunk['chunk_index']}"
                    
                    # Ensure content is included in metadata
                    pinecone_vectors.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {
                            "document_id": doc.id,
                            "user_id": user_id,
                            "chunk_index": chunk["chunk_index"],
                            "page_number": chunk["page_number"],
                            "content": chunk["content"]  # IMPORTANT: Include actual content
                        }
                    })
                
                # Upsert batch to Pinecone
                pinecone_start = time.time()
                print(f"[DOCUMENT] Upserting {len(pinecone_vectors)} vectors to Pinecone...")
                embedding_service.upsert_to_pinecone(pinecone_vectors)
                pinecone_time = time.time() - pinecone_start
                print(f"[DOCUMENT] Batch {batch_num} upserted in {pinecone_time:.2f}s")
                
                # Clear batch data from memory
                del chunk_texts, embeddings, pinecone_vectors
            
            print(f"[DOCUMENT] All {total_batches} batches processed successfully")
            
            print(f"[DOCUMENT] === PROCESSING COMPLETE ===\n")
            return doc

        except Exception as e:
            print(f"[DOCUMENT] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            if doc:
                try:
                    embedding_service.delete_document_embeddings(doc.id)
                except Exception as cleanup_error:
                    print(f"[DOCUMENT] WARNING: Could not remove partial embeddings: {cleanup_error}")
                finally:
                    self.doc_repo.delete(doc)
            PDFService.delete_file(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    def list_user_documents(self, user_id: int) -> List[Document]:
        return self.doc_repo.get_all_by_user(user_id)

    def get_document_details(self, document_id: int, user_id: int) -> Document:
        doc = self.doc_repo.get_by_id(document_id, user_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc

    def delete_document(self, document_id: int, user_id: int) -> None:
        doc = self.get_document_details(document_id, user_id)
        PDFService.delete_file(doc.file_path)
        # Delete embeddings from Pinecone
        embedding_service.delete_document_embeddings(document_id)
        self.doc_repo.delete(doc)
