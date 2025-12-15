import logging
from PIL import Image
import pytesseract
import io
from typing import Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCREngine:
    """
    Wrapper for Tesseract OCR to extract text from images.
    """
    
    def __init__(self, tesseract_cmd: str = None):
        """
        Initialize OCR Engine.
        
        Args:
            tesseract_cmd (str): Optional path to tesseract executable. 
                                 In Docker, usually defaults to 'tesseract'.
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image_input: Union[str, bytes, Image.Image]) -> str:
        """
        Extract text from an image.
        
        Args:
            image_input: File path (str), raw bytes (bytes), or PIL Image object.
            
        Returns:
            str: Extracted text.
        """
        try:
            image = self._load_image(image_input)
            
            # Simple synchronous OCR for now
            # For production, this might need async/queueing if high volume
            text = pytesseract.image_to_string(image)
            
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""

    def _load_image(self, image_input) -> Image.Image:
        """Helper to load PIL Image from various inputs."""
        if isinstance(image_input, Image.Image):
            return image_input
        
        if isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input))
            
        if isinstance(image_input, str):
            return Image.open(image_input)
            
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

if __name__ == "__main__":
    # Test stub
    pass
