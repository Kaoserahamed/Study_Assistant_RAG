# app/services/document_service.py
from typing import List
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

    def process_and_save_document(self, file: UploadFile, user_id: int) -> Document:
        print(f"\n[DOCUMENT] === PROCESSING DOCUMENT ===")
        print(f"[DOCUMENT] File: {file.filename}")
        print(f"[DOCUMENT] User: {user_id}")
        
        file_path = PDFService.save_file(file)
        print(f"[DOCUMENT] Saved to: {file_path}")

        try:
            print(f"[DOCUMENT] Extracting chunks...")
            extract_start = time.time()
            page_count, chunks_data = PDFService.extract_chunks(file_path)
            extract_time = time.time() - extract_start
            
            print(f"[DOCUMENT] Extracted {len(chunks_data)} chunks from {page_count} pages in {extract_time:.2f}s")
            
            if not chunks_data:
                print(f"[DOCUMENT] ERROR: No chunks extracted!")
                raise Exception("No text extracted from PDF")
            
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

            # Generate embeddings for chunks
            print(f"[DOCUMENT] Generating embeddings for {len(chunks_data)} chunks...")
            embed_start = time.time()
            chunk_texts = [chunk["content"] for chunk in chunks_data]
            embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
            embed_time = time.time() - embed_start
            
            print(f"[DOCUMENT] Generated {len(embeddings)} embeddings in {embed_time:.2f}s")
            if embeddings:
                print(f"[DOCUMENT] First embedding dimensions: {len(embeddings[0])}")
            
            # Save chunks to database
            print(f"[DOCUMENT] Saving chunks to database...")
            self.chunk_repo.bulk_create(document_id=doc.id, chunks_data=chunks_data)
            print(f"[DOCUMENT] Chunks saved to database")
            
            # Prepare vectors for Pinecone
            print(f"[DOCUMENT] Preparing vectors for Pinecone...")
            pinecone_vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks_data, embeddings)):
                vector_id = f"doc_{doc.id}_chunk_{chunk['chunk_index']}"
                pinecone_vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "document_id": doc.id,
                        "user_id": user_id,
                        "chunk_index": chunk["chunk_index"],
                        "page_number": chunk["page_number"],
                        "content": chunk["content"]
                    }
                })
            
            print(f"[DOCUMENT] Prepared {len(pinecone_vectors)} vectors for Pinecone")
            if pinecone_vectors:
                print(f"[DOCUMENT] First vector ID: {pinecone_vectors[0]['id']}")
                print(f"[DOCUMENT] Vector size: {len(pinecone_vectors[0]['values'])}")
            
            # Upsert to Pinecone
            print(f"[DOCUMENT] Upserting to Pinecone...")
            pinecone_start = time.time()
            embedding_service.upsert_to_pinecone(pinecone_vectors)
            pinecone_time = time.time() - pinecone_start
            print(f"[DOCUMENT] Pinecone upsert completed in {pinecone_time:.2f}s")
            
            print(f"[DOCUMENT] === PROCESSING COMPLETE ===\n")
            return doc

        except Exception as e:
            print(f"[DOCUMENT] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
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