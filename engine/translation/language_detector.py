from langdetect import detect, DetectorFactory
import logging

DetectorFactory.seed = 0
logger = logging.getLogger(__name__)

class LanguageDetector:
    """
    Detects the language of a given text string.
    """
    @staticmethod
    def detect_language(text: str) -> str:
        try:
            if not text or len(text.strip()) < 2:
                return 'en'
            lang = detect(text)
            return lang
        except Exception as e:
            logger.warning(f"Language detection failed, defaulting to 'en': {e}")
            return 'en'
