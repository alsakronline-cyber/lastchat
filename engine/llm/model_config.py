import os
import logging
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMConfig:
    """
    Configuration and factory for the LLM (Ollama).
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMConfig, cls).__new__(cls)
            cls._instance.model_name = os.getenv("OLLAMA_MODEL", "llama3") # Default to llama3 or mistral
            cls._instance.base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
            cls._instance.temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
            cls._instance._llm = None
        return cls._instance

    def get_llm(self):
        """Returns the configured LLM instance."""
        if self._llm is None:
            logger.info(f"Initializing LLM: {self.model_name} at {self.base_url}")
            try:
                # Use ChatOllama for chat models
                self._llm = ChatOllama(
                    base_url=self.base_url,
                    model=self.model_name,
                    temperature=self.temperature,
                    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
                )
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                raise e
        return self._llm

def get_model():
    """Convenience function to get the LLM model."""
    return LLMConfig().get_llm()
