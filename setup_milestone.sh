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

# 2. Run Migrations
echo "Step 2: Applying Database Migrations..."
# Running alembic via the api container or locally if python is set up
docker-compose exec -T api alembic upgrade head

# 3. Test Scraper
echo "Step 3: Running Test Scrape..."
# Run a sample scrape of SICK products to verify rich data extraction
docker-compose exec -T api python tools/scrapers/sick_scraper.py

# 4. Ingestion & RAG Verification
echo "Step 4: Running Data Ingestion & RAG Verification..."
# (If there is a separate ingestion script, run it here. 
# sick_scraper.py currently saves directly to DB, so we just verify DB)

# Simple Python script to verify data in DB
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
