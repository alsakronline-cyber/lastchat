import logging
import magic # python-magic for mime detection
from typing import Union, Tuple

from engine.multimodal.ocr_engine import OCREngine
from engine.multimodal.pdf_extractor import PDFExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Main entry point for processing uploaded documents (Images or PDFs).
    Routes to appropriate extractor.
    """
    
    def __init__(self):
        self.ocr = OCREngine()
        self.pdf = PDFExtractor()

    def process_file(self, file_content: bytes, filename: str = "") -> Tuple[str, str]:
        """
        Process a file and return its extracted text and detected type.
        
        Args:
            file_content (bytes): Raw file content.
            filename (str): Original filename (optional hint).
            
        Returns:
            Tuple[str, str]: (Extracted Text, Detected Mime Type)
        """
        try:
            # 1. Detect Mime Type
            mime_type = magic.from_buffer(file_content, mime=True)
            logger.info(f"Processing file '{filename}'. Detected mime: {mime_type}")
            
            extracted_text = ""
            
            # 2. Route
            if "pdf" in mime_type:
                extracted_text = self.pdf.extract_text(file_content)
            elif "image" in mime_type:
                extracted_text = self.ocr.extract_text(file_content)
            else:
                logger.warning(f"Unsupported file type: {mime_type}")
                return "", mime_type

            # 3. Post-process (basic cleanup)
            cleaned_text = self._cleanup_text(extracted_text)
            return cleaned_text, mime_type

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise e

    def _cleanup_text(self, text: str) -> str:
        """Remove excessive whitespace and garbage."""
        if not text:
            return ""
        
        # Replace multiple newlines with single
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return "\n".join(lines)

if __name__ == "__main__":
    pass
