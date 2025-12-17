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
    
    # Prioritize DATABASE_URL if set
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        logger.info("Connected to PostgreSQL.")
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return

    # 2. Batch Processing
    BATCH_SIZE = 100
    offset = 0
    total_synced = 0
    
    # Initialize components once
    logger.info("Loading Embedding Model...")
    embedder = EmbeddingModel()
    
    milvus_host = os.getenv("MILVUS_HOST", "localhost")
    logger.info(f"Connecting to Milvus at {milvus_host}...")
    indexer = VectorIndexer(host=milvus_host)
    
    while True:
        logger.info(f"Processing batch: Offset {offset}, Limit {BATCH_SIZE}")
        
        stmt = text("SELECT product_name, sku_id, category, description, specifications FROM products LIMIT :limit OFFSET :offset")
        result = conn.execute(stmt, {"limit": BATCH_SIZE, "offset": offset})
        rows = result.fetchall()
        
        if not rows:
            break
            
        products = []
        texts_to_embed = []
        
        for row in rows:
            p = {
                "product_id": str(row[1]),
                "sku": row[1],
                "name": row[0],
                "category": row[2]
            }
            products.append(p)
            
            # Text for embedding
            specs_str = str(row[4]) if row[4] else ""
            # Truncate specs to avoid token limit errors (bert limit is usually 512 tokens)
            text_content = f"Product: {row[0]}\nCategory: {row[2]}\nDescription: {row[3]}\nSpecs: {specs_str[:1000]}"
            texts_to_embed.append(text_content)
            
        # 3. Generate Embeddings & Insert
        if products:
            try:
                embeddings = embedder.embed_text(texts_to_embed)
                indexer.insert_products(products, embeddings)
                total_synced += len(products)
                logger.info(f"Synced batch of {len(products)} products.")
            except Exception as e:
                logger.error(f"Error syncing batch at offset {offset}: {e}")

        offset += BATCH_SIZE
        
    logger.info(f"Sync Complete! Total Synced: {total_synced}")

if __name__ == "__main__":
    sync_products()
