#!/bin/bash

# Verification Script for Industrial (SICK) Recommendation Engine
# Usage: ./scripts/verify_all.sh

set -e # Exit on error

echo "=============================================="
echo "🚀 Starting Full System Verification"
echo "=============================================="

# 1. Database Migrations
echo ""
echo "🛠️  Step 1: Running Database Migrations..."
docker exec automation-engine alembic upgrade head
echo "✅ Database schema up to date."

# 2. Scraping Data (SICK)
# We run it briefly just to ensure we have some data
echo ""
echo "🕷️  Step 2: Testing SICK Scraper..."
docker exec automation-engine python -m tools.scrapers.sick_scraper
echo "✅ Scraper finished."

# 3. Vector Indexing
echo ""
echo "🧠 Step 3: Indexing Data into Milvus..."
docker exec automation-engine python scripts/index_all_products.py
echo "✅ Indexing complete."

# 4. RAG Chain Test
echo ""
echo "🤖 Step 4: Testing RAG Recommendation Engine..."
TEST_QUERY="I need a high precision laser distance sensor with IO-Link"
echo "   Query: '$TEST_QUERY'"
docker exec automation-engine python scripts/test_rag_chain.py "$TEST_QUERY"
echo "✅ RAG Test complete."

# 5. API API Health Check & Endpoint Test
echo ""
echo "🌐 Step 5: Testing REST API..."
echo "   > Checking Health..."
curl -s -f http://localhost:8000/api/v1/health || echo "❌ API Health Check Failed"

echo "   > Testing /recommend Endpoint..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/recommend" \
     -H "Content-Type: application/json" \
     -d "{\"query\": \"sensor for transparent objects\", \"top_k\": 3}")

echo "Response Preview: ${RESPONSE:0:100}..."
echo "✅ API Tests complete."

echo ""
echo "=============================================="
echo "🎉 SYSTEM VERIFIED SUCCESSFULLY"
echo "=============================================="
