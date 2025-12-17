import os
import sys
import logging
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.embeddings.embedding_model import EmbeddingModel
from engine.embeddings.vector_indexer import VectorIndexer

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyncMilvus")

def sync_products():
    # 1. Connect to DB
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASS = os.getenv("POSTGRES_PASSWORD", "secure_password")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "automation_engine")
    
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        logger.info("Connected to PostgreSQL.")
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return

    # 2. Fetch Products
    # Only fetch fields needed for embedding and metadata
    stmt = text("SELECT product_name, sku_id, category, description, specifications FROM products")
    result = conn.execute(stmt)
    products = []
    texts_to_embed = []
    
    for row in result:
        p = {
            "product_id": str(row[1]), # Using SKU as ID for simplicity
            "sku": row[1],
            "name": row[0],
            "category": row[2]
        }
        products.append(p)
        
        # Construct text for embedding: Name + Description + Specs
        # This provides rich semantic context
        specs_str = str(row[4]) if row[4] else ""
        text_content = f"Product: {row[0]}\nCategory: {row[2]}\nDescription: {row[3]}\nSpecs: {specs_str[:500]}" # Truncate specs to avoid token limit if needed
        texts_to_embed.append(text_content)

    logger.info(f"Fetched {len(products)} products from DB.")
    
    if not products:
        logger.warning("No products to sync.")
        return

    # 3. Generate Embeddings
    logger.info("Loading Embedding Model (this may take a moment)...")
    embedder = EmbeddingModel()
    embeddings = embedder.embed_text(texts_to_embed)
    logger.info(f"Generated {len(embeddings)} embeddings.")

    # 4. Insert into Milvus
    logger.info("Connecting to Milvus...")
    indexer = VectorIndexer(host="localhost") # Default to local
    indexer.insert_products(products, embeddings)
    
    logger.info("Sync Complete!")

if __name__ == "__main__":
    sync_products()
