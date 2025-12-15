import logging
import os
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingModel:
    """
    Wrapper for SentenceTransformer to generate embeddings for product text.
    Uses 'all-MiniLM-L6-v2' by default which provides a good balance of speed and accuracy.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.
        
        Args:
            model_name (str): Name of the model to load from HuggingFace.
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads the SentenceTransformer model, checking for local files first."""
        try:
            # 1. Try Local Path (Docker/Deploy friendly)
            raw_path = os.path.join(os.path.dirname(__file__), "..", "model_data", self.model_name)
            local_path = os.path.abspath(raw_path)
            
            if os.path.exists(local_path) and os.path.isdir(local_path):
                logger.info(f"Loading embedding model from local cache: {local_path}...")
                
                # Debug: List files to ensure mapped correctly
                try:
                    files = os.listdir(local_path)
                    logger.info(f"Files in model dir: {files}")
                except Exception as e:
                    logger.warning(f"Could not list files: {e}")
                
                # Manual loading using transformers directly to avoid HF validation
                from transformers import AutoTokenizer, AutoModel
                import torch
                
                # Load tokenizer and model without any network calls
                tokenizer = AutoTokenizer.from_pretrained(local_path, local_files_only=True)
                model = AutoModel.from_pretrained(local_path, local_files_only=True)
                
                # Wrap in SentenceTransformer-compatible way
                # We create a minimal SentenceTransformer by directly setting its internal model
                self.model = SentenceTransformer.__new__(SentenceTransformer)
                
                # Critical: Initialize the base nn.Sequential to get _parameters, _modules, etc.
                import torch.nn as nn
                nn.Sequential.__init__(self.model)

                from sentence_transformers.models import Transformer, Pooling
                
                # Create transformer wrapper
                transformer = Transformer(
                    model_name_or_path=local_path,
                    tokenizer_name_or_path=local_path,
                    max_seq_length=256
                )
                
                # Create pooling layer (MEAN pooling is default for all-MiniLM-L6-v2)
                pooling = Pooling(
                    transformer.get_word_embedding_dimension(),
                    pooling_mode_mean_tokens=True
                )
                
                # Add modules properly to the Sequential container
                self.model.add_module('0', transformer)
                self.model.add_module('1', pooling)
                
                # Critical: Set device for SentenceTransformer
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.model._target_device = torch.device(device)
                self.model.to(device)
                
                logger.info(f"Embedding model loaded successfully from local cache on {device}.")
                
            else:
                 # 2. Fallback to Download (Will fail in offline Codespace if not cached)
                logger.info(f"Local model not found at {local_path}. Attempting to download: {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
            
        except Exception as e:
            logger.error(f"Failed to load embedding model {self.model_name}: {e}")
            raise e

    def embed_text(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for a string or list of strings.
        
        Args:
            text (str | List[str]): The text(s) to embed.
            
        Returns:
            List[float] | List[List[float]]: The embedding vector(s).
        """
        if not self.model:
            raise RuntimeError("Model not initialized. Call _load_model first.")

        if not text:
            logger.warning("Empty text provided for embedding.")
            return [] if isinstance(text, list) else []

        try:
            embeddings = self.model.encode(text)
            
            # Convert numpy array to list for easier handling/serialization
            if isinstance(embeddings, np.ndarray):
                return embeddings.tolist()
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise e

    def get_dimension(self) -> int:
        """Returns the dimension of the embeddings generated by this model."""
        if not self.model:
            return 0
        return self.model.get_sentence_embedding_dimension()

if __name__ == "__main__":
    # Simple test
    try:
        embedder = EmbeddingModel()
        test_text = "SICK inductive proximity sensor with IO-Link"
        vector = embedder.embed_text(test_text)
        print(f"Generated embedding for '{test_text}'")
        print(f"Dimension: {len(vector)}")
        print(f"First 5 values: {vector[:5]}")
    except Exception as e:
        print(f"Test failed: {e}")
