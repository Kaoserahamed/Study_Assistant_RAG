"""Text extraction and chunking for uploaded study materials."""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Tuple

from docx import Document as DocxDocument
from pypdf import PdfReader
from pptx import Presentation


SUPPORTED_FORMATS = {".pdf", ".docx", ".pptx", ".ppt", ".txt"}
MAX_CHUNK_SIZE = 4_000
MAX_CHUNKS = 10_000


class DocumentProcessor:
    """Extract text while retaining its source page/slide for citations."""

    @staticmethod
    def is_supported(filename: str) -> bool:
        return bool(filename) and os.path.splitext(filename)[1].lower() in SUPPORTED_FORMATS

    @staticmethod
    def get_supported_formats() -> str:
        return ", ".join(fmt[1:].upper() for fmt in sorted(SUPPORTED_FORMATS))

    @staticmethod
    def process_file(file_path: str, chunk_size: int = 1_400, overlap: int = 200) -> Tuple[int, List[Dict[str, Any]]]:
        chunk_size = max(200, min(chunk_size, MAX_CHUNK_SIZE))
        overlap = max(0, min(overlap, chunk_size - 1))
        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".pdf":
            return DocumentProcessor._process_pdf(file_path, chunk_size, overlap)
        if extension == ".docx":
            return DocumentProcessor._process_docx(file_path, chunk_size, overlap)
        if extension == ".pptx":
            return DocumentProcessor._process_pptx(file_path, chunk_size, overlap)
        if extension == ".ppt":
            raise ValueError("Legacy .ppt files are not supported. Please save the file as .pptx.")
        if extension == ".txt":
            return 1, DocumentProcessor._chunk_text(DocumentProcessor._read_text(file_path), 1, chunk_size, overlap)
        raise ValueError(f"Unsupported file format: {extension}")

    @staticmethod
    def _read_text(file_path: str) -> str:
        # utf-8-sig handles files saved by Windows applications with a BOM.
        with open(file_path, "r", encoding="utf-8-sig", errors="replace") as source:
            return source.read()

    @staticmethod
    def _normalise_text(text: str) -> str:
        text = text.replace("\u00ad", "")  # soft hyphen commonly emitted by PDFs
        text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)  # join hyphenated line wraps
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n[ \t]*\n+", "\n\n", text)
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
        return text.strip()

    @staticmethod
    def _chunk_text(text: str, page_number: int, chunk_size: int, overlap: int, start_index: int = 0) -> List[Dict[str, Any]]:
        """Chunk one source unit. Always advances, including a short last chunk."""
        text = DocumentProcessor._normalise_text(text)
        if not text:
            return []

        chunks: List[Dict[str, Any]] = []
        start = 0
        while start < len(text) and len(chunks) < MAX_CHUNKS:
            end = min(start + chunk_size, len(text))
            if end < len(text):
                # Prefer a paragraph, sentence, or word boundary near the limit.
                boundary_start = start + int(chunk_size * 0.55)
                candidates = [
                    text.rfind("\n\n", boundary_start, end),
                    text.rfind(". ", boundary_start, end),
                    text.rfind("? ", boundary_start, end),
                    text.rfind("! ", boundary_start, end),
                    text.rfind(" ", boundary_start, end),
                ]
                boundary = max(candidates)
                if boundary > start:
                    end = boundary + (2 if text[boundary:boundary + 2] == "\n\n" else 1)

            content = text[start:end].strip()
            if content:
                chunks.append({
                    "page_number": page_number,
                    "chunk_index": start_index + len(chunks),
                    "content": content,
                })
            if end >= len(text):
                break
            # Do not let overlap make the cursor stall or move backward.
            start = max(end - overlap, start + 1)
        return chunks

    @staticmethod
    def _process_pdf(file_path: str, chunk_size: int, overlap: int) -> Tuple[int, List[Dict[str, Any]]]:
        reader = PdfReader(file_path)
        if reader.is_encrypted:
            if reader.decrypt("") == 0:
                raise ValueError("This PDF is password protected. Upload an unlocked copy.")

        chunks: List[Dict[str, Any]] = []
        for page_number, page in enumerate(reader.pages, start=1):
            if len(chunks) >= MAX_CHUNKS:
                break
            try:
                page_text = page.extract_text(extraction_mode="layout") or ""
            except TypeError:  # pypdf versions before layout extraction
                page_text = page.extract_text() or ""
            except Exception as error:
                raise ValueError(f"Could not extract text from PDF page {page_number}: {error}") from error
            # Do not silently discard the tail of a text-heavy page.  The global
            # MAX_CHUNKS guard below is the intentional document-size limit.
            page_chunks = DocumentProcessor._chunk_text(
                page_text, page_number, chunk_size, overlap, len(chunks)
            )
            chunks.extend(page_chunks[:MAX_CHUNKS - len(chunks)])
        return len(reader.pages), chunks

    @staticmethod
    def _process_docx(file_path: str, chunk_size: int, overlap: int) -> Tuple[int, List[Dict[str, Any]]]:
        document = DocxDocument(file_path)
        text = "\n\n".join(p.text for p in document.paragraphs if p.text.strip())
        return 1, DocumentProcessor._chunk_text(text, 1, chunk_size, overlap)

    @staticmethod
    def _process_pptx(file_path: str, chunk_size: int, overlap: int) -> Tuple[int, List[Dict[str, Any]]]:
        presentation = Presentation(file_path)
        chunks: List[Dict[str, Any]] = []
        for slide_number, slide in enumerate(presentation.slides, start=1):
            slide_text = "\n".join(shape.text for shape in slide.shapes if getattr(shape, "text", "").strip())
            chunks.extend(DocumentProcessor._chunk_text(slide_text, slide_number, chunk_size, overlap, len(chunks)))
        return len(presentation.slides), chunks
