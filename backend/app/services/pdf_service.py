# app/services/pdf_service.py
import os
import uuid
from pypdf import PdfReader
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class PDFService:
    @staticmethod
    def save_file(file: UploadFile) -> str:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        return file_path

    @staticmethod
    def extract_chunks(file_path: str, chunk_size: int = 800, overlap: int = 100):
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        chunks_data = []
        global_chunk_index = 0

        step = chunk_size - overlap

        for page_num, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            if not text:
                continue

            start = 0

            while start < len(text):
                end = min(start + chunk_size, len(text))

                # Avoid cutting in the middle of a word
                if end < len(text):
                    whitespace_pos = text.rfind(" ", start, end)

                    if whitespace_pos > start:
                        end = whitespace_pos

                content = text[start:end].strip()

                if content:
                    chunks_data.append({
                        "page_number": page_num,
                        "chunk_index": global_chunk_index,
                        "content": content,
                    })

                    global_chunk_index += 1

                # Make sure progress always happens
                start = end - overlap

        return page_count, chunks_data
        
    @staticmethod
    def delete_file(file_path: str) -> None:
        if os.path.exists(file_path):
            os.remove(file_path)