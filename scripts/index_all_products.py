import sys
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import time

# Add project root to sys.path
sys.path.append(os.getcwd())

from engine.embeddings.search_engine import SearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database config
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "automation_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def index_all_products():
    """
    Fetches all products from PostgreSQL and re-indexes them in Milvus.
    """
    logger.info("Starting bulk indexing job...")
    
    # 1. Initialize Search Engine
    try:
        search_engine = SearchEngine()
        logger.info("Search Engine initialized.")
    except Exception as e:
        logger.error(f"Failed to init Search Engine: {e}")
        return

    # 2. Connect to Database (using raw SQL for simplicity/speed)
    engine = create_engine(DATABASE_URL)
    
    # 3. Fetch Products
    batch_size = 100
    offset = 0
    total_indexed = 0
    
    with engine.connect() as conn:
        try:
            # Count total
            count_res = conn.execute(text("SELECT COUNT(*) FROM products"))
            total_products = count_res.scalar()
            logger.info(f"Total products to index: {total_products}")
            
            while True:
                # Fetch batch
                # Assuming 'id' is the primary key (UUID) and stored as string
                query = text(f"""
                    SELECT id, sku_id, product_name, category, description, specifications 
                    FROM products 
                    ORDER BY created_at DESC 
                    LIMIT {batch_size} OFFSET {offset}
                """)
                result = conn.execute(query)
                rows = result.fetchall()
                
                if not rows:
                    break
                
                # Convert to list of dicts for SearchEngine
                products_batch = []
                for row in rows:
                    products_batch.append({
                        "product_id": str(row[0]), # UUID to string
                        "sku": row[1],
                        "name": row[2],
                        "category": row[3],
                        "description": row[4] or "" # Handle NULLs
                    })
                
                logger.info(f"Indexing batch {offset} to {offset + len(products_batch)}...")
                
                # 4. Index Batch
                search_engine.index_product_batch(products_batch)
                
                total_indexed += len(products_batch)
                offset += batch_size
                
                # Sleep briefly to give CPU a break if needed
                # time.sleep(0.1)

            logger.info(f"Bulk indexing complete. Total indexed: {total_indexed}")

        except Exception as e:
            logger.error(f"Database error: {e}")
            raise e

if __name__ == "__main__":
    # Wait for DB services to be fully ready if running in docker-compose startup
    # time.sleep(5) 
    index_all_products()
