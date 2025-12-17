#!/bin/bash
set -e

echo "=== SICK Data Pipeline Setup =="

# 1. Clean Environment
echo "Step 1: Restarting services and cleaning DB..."
# We use docker-compose to restart services. 
# CAUTION: 'down -v' deletes volumes (data).
docker-compose down -v
docker-compose up -d --build

echo "Waiting for PostgreSQL to be ready..."
sleep 10 # Basic wait, could be improved with healthcheck loop

# 1.5 Pull LLM Model
echo "Step 1.5: Pulling LLM Model (tinyllama)..."
docker-compose exec -T ollama ollama pull tinyllama

# 2. Run Migrations
echo "Step 2: Applying Database Migrations..."
# Running alembic via the api container to the SPECIFIC new revision
# This avoids "Multiple heads" error if there are stray migrations in the user's env
docker-compose exec -T api alembic upgrade 2e9c2f6d0a7b

# 3. Test Scraper
echo "Step 3: Running Test Scrape..."
# Run a sample scrape of SICK products to verify rich data extraction
# Run as module to allow relative imports
docker-compose exec -T api python -m tools.scrapers.sick_scraper

# 4. Ingestion & RAG Verification
echo "Step 4: Syncing DB to Milvus (Embedding)..."
docker-compose exec -T api python -m tools.sync_db_to_milvus

# 5. RAG Verification
echo "Step 5: Testing RAG Retrieval..."
docker-compose exec -T api python -c "
from sqlalchemy import create_engine, text
import os
import json

db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
with engine.connect() as conn:
    result = conn.execute(text('SELECT product_name, documents, technical_drawings FROM products LIMIT 5'))
    rows = result.fetchall()
    print(f'\n[VERIFICATION] Found {len(rows)} products in DB:')
    for row in rows:
        print(f' - {row[0]}')
        print(f'   Docs: {len(row[1]) if row[1] else 0}, Drawings: {len(row[2]) if row[2] else 0}')
"

echo "=== Setup Complete! ==="

# 5. RAG Verification
echo "Step 5: Testing RAG Retrieval..."
docker-compose exec -T api python -c "
try:
    from engine.rag.recommendation_chain import RecommendationChain
    rag = RecommendationChain()
    print('\n[TEST] Querying: \"Find fiber optic cables with drawings\"')
    result = rag.get_recommendation('Find fiber optic cables with drawings')
    print('\n--- AI Response ---')
    print(result['answer'])
    print('-------------------')
except Exception as e:
    print(f'[ERROR] RAG Test Failed: {e}')
"
