import csv
import os
import logging
from typing import Optional
from sqlalchemy import create_engine, text
import json
import ast

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CSV_Importer")

# Database Connection
# Use 'localhost' if running from host/codespace terminal, or 'postgres' if running from inside docker network.
# Default to localhost for external script usage.
DB_USER = "postgres"
DB_PASS = "secure_password"
DB_HOST = "localhost" # or 'postgres' inside docker
DB_PORT = "5432"
DB_NAME = "automation_engine"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def import_csv(filename: str):
    if not os.path.exists(filename):
        logger.error(f"File {filename} not found.")
        return

    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        logger.info(f"Connected to Database: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"DB Connection Failed: {e}")
        return

    success_count = 0
    
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            sku = row.get("sku_id")
            name = row.get("product_name")
            image_url = row.get("images", "")
            specs_str = row.get("specifications", "{}")
            datasheet = row.get("datasheet_url", "")
            
            # Clean image string if it's a list representation
            images_list = []
            if image_url:
                try:
                    images_list = ast.literal_eval(image_url) if image_url.startswith("[") else [image_url]
                except:
                    images_list = [image_url]
            
            # Parse Specifications JSON
            specs_json = {}
            if specs_str:
                try:
                    # CSV parses it as string with single quotes often if from python dict, using ast to be safe
                    specs_json = ast.literal_eval(specs_str) if specs_str.startswith("{") else json.loads(specs_str)
                except:
                    specs_json = {}

            if not sku or sku == "Unknown":
                logger.warning(f"Skipping row with invalid SKU: {row}")
                continue

            # UPSERT Query
            sql = text("""
                INSERT INTO products (sku_id, product_name, images, source, specifications, datasheet_url, created_at)
                VALUES (:sku_id, :product_name, :images, :source, :specifications, :datasheet_url, NOW())
                ON CONFLICT (sku_id) DO UPDATE 
                SET product_name = EXCLUDED.product_name, 
                    images = EXCLUDED.images,
                    specifications = EXCLUDED.specifications,
                    datasheet_url = EXCLUDED.datasheet_url;
            """)
            
            try:
                conn.execute(sql, {
                    "sku_id": sku,
                    "product_name": name,
                    "images": json.dumps(images_list), 
                    "source": row.get("source", ""),
                    "specifications": json.dumps(specs_json),
                    "datasheet_url": datasheet
                })
                conn.commit()
                success_count += 1
                logger.debug(f"Imported {sku}")
            except Exception as e:
                logger.error(f"Failed to insert {sku}: {e}")
                conn.rollback()

    logger.info(f"Import Complete. Successfully imported {success_count} products.")
    conn.close()

if __name__ == "__main__":
    import_csv("scraped_data.csv")
