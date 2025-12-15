import logging
from typing import List, Dict
from engine.embeddings.embedding_model import EmbeddingModel
from engine.embeddings.vector_indexer import VectorIndexer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchEngine:
    """
    High-level interface for semantic product search.
    Combines EmbeddingModel and VectorIndexer.
    """
    
    def __init__(self):
        self.embedder = EmbeddingModel()
        self.indexer = VectorIndexer()
        # Ensure collection exists and is ready
        dim = self.embedder.get_dimension()
        self.indexer.create_collection(dim=dim)

    def search_products(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for products semantically matching the query.
        
        Args:
            query (str): User's search text.
            limit (int): Number of results to return.
            
        Returns:
            List[Dict]: List of matching products with scores.
        """
        logger.info(f"Searching for: '{query}'")
        
        # 1. Generate embedding for the query
        query_vec = self.embedder.embed_text(query)
        if not query_vec:
            return []

        # 2. Search in Milvus
        results = self.indexer.search(query_vec, top_k=limit)
        
        logger.info(f"Found {len(results)} matches.")
        return results

    def index_product_batch(self, products: List[Dict]):
        """
        Index a batch of products effectively.
        
        Args:
           products (List[Dict]): List of product dicts. Must have 'product_id', 'sku', 'name'. 
                                  'description' or 'specifications' recommended for better embeddings.
        """
        if not products:
            return

        # 1. Prepare text for embedding
        # We combine important fields to create a rich semantic representation
        texts_to_embed = []
        for p in products:
            # Combine Name + Category + Description (if available)
            text = f"{p.get('name', '')} {p.get('category', '')} {p.get('description', '')}"
            texts_to_embed.append(text.strip())

        # 2. Generate embeddings
        embeddings = self.embedder.embed_text(texts_to_embed)

        # 3. Insert into Milvus
        self.indexer.insert_products(products, embeddings)

if __name__ == "__main__":
    # Simple test
    try:
        engine = SearchEngine()
        
        # Mock indexing
        mock_products = [
            {"product_id": "1", "sku": "SICK-100", "name": "Inductive Proximity Sensor", "category": "Sensors"},
            {"product_id": "2", "sku": "SICK-200", "name": "Safety Light Curtain", "category": "Safety"},
        ]
        engine.index_product_batch(mock_products)
        
        # Mock search
        results = engine.search_products("safety sensor")
        for res in results:
            print(f"Match: {res['name']} (Score: {res['score']:.4f})")
            
    except Exception as e:
        print(f"Test failed: {e}")
