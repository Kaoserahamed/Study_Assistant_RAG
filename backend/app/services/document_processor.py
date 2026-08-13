# app/services/document_processor.py
from typing import Tuple, List, Dict, Any
import os
from pypdf import PdfReader
from docx import Document as DocxDocument
from pptx import Presentation

SUPPORTED_FORMATS = {".pdf", ".docx", ".pptx", ".ppt", ".txt"}


class DocumentProcessor:
    """Unified processor for multiple document formats"""
    
    @staticmethod
    def is_supported(filename: str) -> bool:
        """Check if file format is supported"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in SUPPORTED_FORMATS
    
    @staticmethod
    def get_supported_formats() -> str:
        """Return comma-separated list of supported formats"""
        return ", ".join([fmt[1:].upper() for fmt in sorted(SUPPORTED_FORMATS)])
    
    @staticmethod
    def process_file(file_path: str, chunk_size: int = 2000, overlap: int = 400) -> Tuple[int, List[Dict[str, Any]]]:
        """Process any supported file format and return page count and chunks
        
        Args:
            file_path: Path to the file to process
            chunk_size: Size of each chunk in characters (default 2000 - about 300-400 words)
            overlap: Number of characters to overlap between chunks (default 400)
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return DocumentProcessor._process_pdf(file_path, chunk_size, overlap)
        elif ext == ".docx":
            return DocumentProcessor._process_docx(file_path, chunk_size, overlap)
        elif ext == ".pptx":
            return DocumentProcessor._process_pptx(file_path, chunk_size, overlap)
        elif ext == ".ppt":
            return DocumentProcessor._process_ppt(file_path, chunk_size, overlap)
        elif ext == ".txt":
            return DocumentProcessor._process_txt(file_path, chunk_size, overlap)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @staticmethod
    def _process_pdf(file_path: str, chunk_size: int, overlap: int) -> Tuple[int, List[Dict[str, Any]]]:
        """Process PDF files with smart chunking at sentence boundaries"""
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        chunks_data = []
        global_chunk_index = 0
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            
            # Split by sentences/periods to avoid breaking mid-sentence
            # Replace common sentence endings with a marker
            text = text.replace('\n\n', ' [PARA] ')  # Paragraph breaks
            text = text.replace('\n', ' ')  # Line breaks to spaces
            
            # Create chunks while trying to respect boundaries
            start = 0
            while start < len(text):
                # Try to get chunk_size characters
                end = min(start + chunk_size, len(text))
                
                # If not at end of text, try to find a good break point (period, newline, etc)
                if end < len(text):
                    # Look backward for sentence end within last 200 chars
                    last_period = text.rfind('. ', max(start, end - 200), end)
                    last_para = text.rfind('[PARA]', max(start, end - 200), end)
                    
                    # Use whichever comes last (closest to end)
                    break_point = max(last_period, last_para)
                    if break_point > start + chunk_size * 0.5:  # At least 50% of chunk size
                        end = break_point + 1
                
                chunk_text = text[start:end].strip()
                if chunk_text:  # Only add non-empty chunks
                    chunks_data.append({
                        "page_number": page_num,
                        "chunk_index": global_chunk_index,
                        "content": chunk_text
                    })
                    global_chunk_index += 1
                
                # Move start position for next chunk (with overlap)
                start = end - overlap
        
        return page_count, chunks_data
    
    @staticmethod
    def _process_docx(file_path: str, chunk_size: int, overlap: int) -> Tuple[int, List[Dict[str, Any]]]:
        """Process DOCX files with paragraph-aware chunking"""
        doc = DocxDocument(file_path)
        chunks_data = []
        global_chunk_index = 0
        page_num = 1
        
        # Collect all paragraphs first
        all_text = []
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                all_text.append(text)
        
        # Join paragraphs and chunk
        full_text = '\n\n'.join(all_text)
        
        start = 0
        while start < len(full_text):
            end = min(start + chunk_size, len(full_text))
            
            # Try to break at paragraph boundary if not at end
            if end < len(full_text):
                last_para = full_text.rfind('\n\n', max(start, end - 200), end)
                last_period = full_text.rfind('. ', max(start, end - 200), end)
                break_point = max(last_para, last_period)
                if break_point > start + chunk_size * 0.5:
                    end = break_point + (2 if full_text[break_point:break_point+2] == '\n\n' else 1)
            
            chunk_text = full_text[start:end].strip()
            if chunk_text:
                chunks_data.append({
                    "page_number": page_num,
                    "chunk_index": global_chunk_index,
                    "content": chunk_text
                })
                global_chunk_index += 1
            
            start = end - overlap
        
        return page_num, chunks_data
    
    @staticmethod
    def _process_pptx(file_path: str, chunk_size: int, overlap: int) -> Tuple[int, List[Dict[str, Any]]]:
        """Process PPTX files with smart slide chunking"""
        prs = Presentation(file_path)
        chunks_data = []
        global_chunk_index = 0
        
        for slide_num, slide in enumerate(prs.slides, start=1):
            slide_text = ""
            
            # Extract text from all shapes, preserving structure
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text:
                    slide_text += shape.text + "\n"
            
            slide_text = slide_text.strip()
            if not slide_text:
                continue
            
            # For presentations, each slide with its text is often a good chunk
            # But split if very large
            if len(slide_text) <= chunk_size:
                chunks_data.append({
                    "page_number": slide_num,
                    "chunk_index": global_chunk_index,
                    "content": slide_text
                })
                global_chunk_index += 1
            else:
                # Split large slides at sentence boundaries
                start = 0
                while start < len(slide_text):
                    end = min(start + chunk_size, len(slide_text))
                    
                    if end < len(slide_text):
                        last_period = slide_text.rfind('. ', max(start, end - 200), end)
                        if last_period > start + chunk_size * 0.5:
                            end = last_period + 1
                    
                    chunk_text = slide_text[start:end].strip()
                    if chunk_text:
                        chunks_data.append({
                            "page_number": slide_num,
                            "chunk_index": global_chunk_index,
                            "content": chunk_text
                        })
                        global_chunk_index += 1
                    
                    start = end - overlap
        
        return len(prs.slides), chunks_data
    
    @staticmethod
    def _process_ppt(file_path: str, chunk_size: int, overlap: int) -> Tuple[int, List[Dict[str, Any]]]:
        """Process PPT files (older format) - treat as PPTX"""
        # Python-pptx doesn't support old PPT format natively
        # This is a fallback - in production, you'd use python-ppt or libreoffice conversion
        raise NotImplementedError("PPT (old format) support requires additional conversion. Use PPTX format instead.")
    
    @staticmethod
    def _process_txt(file_path: str, chunk_size: int, overlap: int) -> Tuple[int, List[Dict[str, Any]]]:
        """Process TXT files with paragraph-aware chunking"""
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        chunks_data = []
        global_chunk_index = 0
        page_num = 1
        
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to break at paragraph or sentence boundary
            if end < len(text):
                # Look for paragraph break first (double newline)
                last_para = text.rfind('\n\n', max(start, end - 200), end)
                # Then look for period and newline
                last_period = text.rfind('.\n', max(start, end - 200), end)
                # Then just a period
                last_period_only = text.rfind('. ', max(start, end - 200), end)
                
                break_point = max(last_para, last_period, last_period_only)
                if break_point > start + chunk_size * 0.5:
                    end = break_point + (2 if text[break_point:break_point+2] in ['\n\n', '.\n'] else 1)
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks_data.append({
                    "page_number": page_num,
                    "chunk_index": global_chunk_index,
                    "content": chunk_text
                })
                global_chunk_index += 1
            
            start = end - overlap
        
        return page_num, chunks_data
