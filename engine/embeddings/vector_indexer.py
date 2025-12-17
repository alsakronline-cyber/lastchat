import logging
from typing import List, Dict, Any
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorIndexer:
    """
    Manages the Milvus vector database connection and indexing operations.
    """
    
    def __init__(self, host: str = "localhost", port: str = "19530", collection_name: str = "products"):
        self.host = os.getenv("MILVUS_HOST", host)
        self.port = os.getenv("MILVUS_PORT", port)
        self.collection_name = collection_name
        self.collection = None
        self._connect()

    def _connect(self):
        """Establish connection to Milvus."""
        try:
            logger.info(f"Connecting to Milvus at {self.host}:{self.port}...")
            connections.connect("default", host=self.host, port=self.port)
            logger.info("Connected to Milvus.")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise e

    def create_collection(self, dim: int = 384):
        """
        Create the product collection if it doesn't exist.
        
        Args:
            dim (int): Dimension of the embedding vectors (default 384 for all-MiniLM-L6-v2).
        """
        if utility.has_collection(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' already exists.")
            self.collection = Collection(self.collection_name)
            self.collection.load() # Load into memory for searching
            return

        logger.info(f"Creating collection '{self.collection_name}' with dim={dim}...")
        
        # Define fields
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True), # Internal Milvus ID
            FieldSchema(name="product_id", dtype=DataType.VARCHAR, max_length=64), # Our DB Product ID (UUID)
            FieldSchema(name="sku", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
        ]
        
        schema = CollectionSchema(fields, "Product embeddings for semantic search")
        self.collection = Collection(self.collection_name, schema)
        
        # Create user-friendly index for faster search
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        logger.info(f"Collection '{self.collection_name}' created and indexed.")
        self.collection.load()

    def insert_products(self, products: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Insert products and their embeddings into Milvus.
        
        Args:
            products (List[Dict]): List of product dictionaries (must contain product_id, sku, name, category).
            embeddings (List[List[float]]): Corresponding list of embedding vectors.
        """
        if not self.collection:
            self.create_collection(dim=len(embeddings[0]))

        if len(products) != len(embeddings):
            raise ValueError("Number of products must match number of embeddings.")

        # Prepare data columns for Milvus (row-based to column-based)
        data = [
            [p["product_id"] for p in products],
            [p["sku"] for p in products],
            [p["name"] for p in products],
            [str(p.get("category", "Uncategorized")) for p in products], # Handle None
            embeddings
        ]

        try:
            res = self.collection.insert(data)
            self.collection.flush() # Ensure data is persisted
            logger.info(f"Inserted {len(products)} vectors. IDs: {res.primary_keys}")
        except Exception as e:
            logger.error(f"Failed to insert vectors: {e}")
            raise e

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar products using a query embedding.
        """
        if not self.collection:
            raise RuntimeError("Collection not initialized.")

        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["product_id", "sku", "name", "category"]
        )

        hits = []
        for hits_i in results:
            for hit in hits_i:
                hits.append({
                    "milvus_id": hit.id,
                    "score": hit.distance,
                    "product_id": hit.entity.get("product_id"),
                    "sku": hit.entity.get("sku"),
                    "name": hit.entity.get("name"),
                    "category": hit.entity.get("category")
                })
        
        return hits
