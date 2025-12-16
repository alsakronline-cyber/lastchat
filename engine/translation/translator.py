from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

class AutoTranslator:
    """
    Handles translation between Arabic and English.
    """
    def __init__(self):
        self.en_to_ar = GoogleTranslator(source='en', target='ar')
        self.ar_to_en = GoogleTranslator(source='ar', target='en')

    def translate_to_english(self, text: str) -> str:
        """Translates Arabic text to English."""
        try:
            if not text or not text.strip():
                return text
            return self.ar_to_en.translate(text)
        except Exception as e:
            logger.error(f"Translation to English failed: {e}")
            return text

    def translate_to_arabic(self, text: str) -> str:
        """Translates English text to Arabic."""
        try:
            if not text or not text.strip():
                return text
            return self.en_to_ar.translate(text)
        except Exception as e:
            logger.error(f"Translation to Arabic failed: {e}")
            return text
