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
        Performs Hybrid Retrieval: Milvus (Vector) -> PostgreSQL (Metadata).
        
        Args:
            query (str): User's search text.
            limit (int): Number of results to return.
            
        Returns:
            List[Dict]: List of matching products with scores and full metadata.
        """
        logger.info(f"Searching for: '{query}'")
        
        # 1. Generate embedding for the query
        query_vec = self.embedder.embed_text(query)
        if not query_vec:
            return []

        # 2. Search in Milvus
        milvus_results = self.indexer.search(query_vec, top_k=limit)
        
        if not milvus_results:
            logger.info("No results found in Milvus.")
            return []
            
        logger.info(f"Found {len(milvus_results)} matches in Milvus. Fetching details from DB...")
        
        # 3. Fetch Reach Metadata from PostgreSQL
        # Extract SKUs to query DB
        sku_map = {res['sku']: res for res in milvus_results}
        skus = list(sku_map.keys())
        
        if not skus:
            return milvus_results

        try:
            from api.database import engine
            from sqlalchemy import text
            import json
            
            # Use a safe parameterized query
            # We must handle the list parameter correctly for IN clause
            # SQLAlchemy text() with bindparams is one way, or simple string formatting if careful.
            # ideally use :skus and tuple(skus)
            
            with engine.connect() as conn:
                stmt = text("""
                    SELECT sku_id, technical_drawings, documents, specifications, images, datasheet_url 
                    FROM products 
                    WHERE sku_id = ANY(:skus)
                """)
                # Execute
                db_results = conn.execute(stmt, {"skus": skus}).fetchall()
                
                # Merge DB data into Milvus results
                for row in db_results:
                    sku = row[0]
                    if sku in sku_map:
                        product = sku_map[sku]
                        product['technical_drawings'] = row[1] if row[1] else []
                        product['documents'] = row[2] if row[2] else []
                        product['specifications'] = row[3] if row[3] else {}
                        product['images'] = row[4] if row[4] else []
                        product['datasheet_url'] = row[5]
                        
        except Exception as e:
            logger.error(f"Failed to fetch metadata from DB: {e}")
            # Fallback: return what we have from Milvus
        
        return milvus_results

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
