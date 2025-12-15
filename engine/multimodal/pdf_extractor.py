import logging
import io
from typing import Union
from PyPDF2 import PdfReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Extracts text from PDF documents.
    """
    
    def extract_text(self, pdf_input: Union[str, bytes], max_pages: int = 10) -> str:
        """
        Extract text from a PDF.
        
        Args:
            pdf_input: File path (str) or raw bytes (bytes).
            max_pages (int): Limit pages to process to avoid timeouts on large manuals.
            
        Returns:
            str: Extracted text combined.
        """
        try:
            reader = self._get_reader(pdf_input)
            
            text_content = []
            
            # Limit pages
            total_pages = len(reader.pages)
            pages_to_read = min(total_pages, max_pages)
            
            for i in range(pages_to_read):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    text_content.append(text)
            
            combined_text = "\n".join(text_content)
            return combined_text.strip()
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""

    def _get_reader(self, pdf_input) -> PdfReader:
        """Helper to get PdfReader."""
        if isinstance(pdf_input, bytes):
            return PdfReader(io.BytesIO(pdf_input))
        
        if isinstance(pdf_input, str):
            return PdfReader(pdf_input)
            
        raise ValueError(f"Unsupported PDF input type: {type(pdf_input)}")

if __name__ == "__main__":
    pass
