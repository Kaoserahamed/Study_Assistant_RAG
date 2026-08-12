# app/services/document_service.py
from typing import List
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
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
        file_path = PDFService.save_file(file)

        try:
            page_count, chunks_data = PDFService.extract_chunks(file_path)

            doc = self.doc_repo.create(
                user_id=user_id,
                filename=file.filename,
                file_path=file_path,
                page_count=page_count
            )

            # Generate embeddings for chunks
            chunk_texts = [chunk["content"] for chunk in chunks_data]
            embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
            
            # Save chunks to database
            self.chunk_repo.bulk_create(document_id=doc.id, chunks_data=chunks_data)
            
            # Prepare vectors for Pinecone
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
            
            # Upsert to Pinecone
            embedding_service.upsert_to_pinecone(pinecone_vectors)
            return doc

        except Exception as e:
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