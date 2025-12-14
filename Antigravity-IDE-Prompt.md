# Professional Multi-Phase Prompt for Antigravity IDE
## Building Industrial Automation AI Recommendation Engine

**Project:** Alsakronline Industrial Automation AI Product Recommendation System  
**Timeline:** Week 1 (MVP) → 1 Month (Production)  
**Target:** Build, test, and deploy production-ready system  

---

## PHASE 1: FOUNDATION & INFRASTRUCTURE SETUP
### Goal: Deploy containerized services and establish data infrastructure

**Prompt for Antigravity IDE:**

```
You are a professional DevOps & Backend Infrastructure Engineer. Your task is to 
architect and generate complete, production-ready infrastructure code for an 
industrial automation AI recommendation system.

REQUIREMENTS:
1. Create Docker Compose configuration for multi-service deployment:
   - PostgreSQL 15 (product database, 100K+ records, GDPR-compliant)
   - Milvus vector database (semantic search, 768-dim embeddings)
   - Redis (task queue for async operations)
   - Ollama (LLM inference server for Llama2-7B)
   - Custom FastAPI Python service (Docker image)

2. Generate PostgreSQL schema with:
   - Products table (sku_id, product_name, manufacturer, specifications JSONB, 
     relationships JSONB, embedding_text, datasheet_url, images, pricing, 
     confidence_score, language, source, created_at)
   - CRM contacts table (contact_id, name, email, company, phone, industry, 
     country, preferences JSONB, timestamps)
   - Quotations table (quotation_id, contact_id, sku_list JSONB, quantities JSONB, 
     delivery_country, status, total_price, expiry)
   - Interaction log table (user_id, query, recommended_sku, confidence_score, 
     response_time_ms, timestamp) with proper indexing
   - Ensure GDPR compliance (encryption, retention policies)

3. Create Dockerfile with:
   - Python 3.11 slim base
   - System dependencies (postgresql-client, tesseract-ocr, libsm6, libxext6)
   - Requirements installation
   - Health check endpoint
   - Non-root user execution

4. Generate docker-compose.yml with:
   - Service networking (internal network for inter-service communication)
   - Volume mounts for persistent data
   - Environment variable configuration
   - Health checks and dependencies
   - Resource limits (CPU, memory)

5. Create Alembic migration scripts for:
   - Initial schema creation
   - Index creation for performance
   - JSONB field configurations
   - Audit trail tables

OUTPUT: 
- docker-compose.yml (complete, production-ready)
- Dockerfile (optimized)
- requirements.txt (all Python dependencies)
- alembic/env.py + migration files
- .env.example file
- deployment/deploy.sh bash script
- README with deployment instructions

QUALITY REQUIREMENTS:
- All code must be production-ready (error handling, logging, security)
- Include comprehensive comments
- Database schema must support 100K+ records with <500ms queries
- Security: encrypted connections, secret management
- Output must be copy-paste ready for deployment to Hostinger

LANGUAGE: Generate all code in English with clear variable names.
```

---

## PHASE 2: DATA PIPELINE & SCRAPING ARCHITECTURE
### Goal: Build ETL for ingesting 100K+ products from multiple sources

**Prompt for Antigravity IDE:**

```
You are a Data Engineering specialist with deep expertise in web scraping, 
ETL pipelines, and data quality. Your task is to generate a complete data 
ingestion and transformation system for industrial automation products.

REQUIREMENTS:

1. Build modular web scrapers for:
   
   a) ABB Products (https://new.abb.com/products)
      - Parse product pages with Selenium + BeautifulSoup
      - Extract: name, SKU, specifications, datasheet URL, images
      - Handle pagination (100+ pages)
      - Rate limiting (respectful crawling, 1-2 requests/second)
      - Retry logic with exponential backoff
   
   b) SICK Sensors (https://www.sick.com/)
      - Web scraping with Selenium
      - Extract: model, technical specs, certifications, datasheet
      - Handle dynamic content loading
   
   c) Siemens Automation (https://www.siemens.com/automation)
      - Parse product categories (SIMATIC, SINUMERIK, SIMOTION, SITOP)
      - Extract: product series, technical data, certifications
   
   d) Schneider Electric (https://www.se.com)
      - Scrape automation products by category
   
   e) Murrelektronik (https://www.murrelektronik.com/)
      - Component scraping (connectors, power supplies, safety)
   
   f) CSV/JSON Manual Import
      - Support batch uploads from partners
      - Flexible schema mapping
      - Duplicate detection and deduplication

2. Create unified data model with standardized schema:
   - All sources → single canonical format
   - Field mapping configuration (YAML-based)
   - Data normalization and cleanup
   - Automatic category inference

3. Build data validation & enrichment pipeline:
   - Schema validation (jsonschema)
   - Required field checks
   - URL validation and verification
   - Image availability checks
   - Datasheet accessibility verification
   - Automatic embedding text generation for RAG
   - Confidence scoring (0.0-1.0) based on data completeness

4. Create data transformation layer:
   - ETL orchestration using n8n-ready format
   - Batch size optimization (100-1000 records)
   - Transaction management (rollback on errors)
   - Incremental updates (only new/changed products)
   - Change data capture (CDC) for updates

5. Build scheduler & monitoring:
   - Weekly scraping schedule configuration
   - Error handling with notifications
   - Logging (structured JSON logs)
   - Metrics: records scraped, success rate, processing time
   - Dry-run mode for testing

6. Data quality checks:
   - Duplicate detection
   - Pricing anomaly detection
   - Missing specification fields
   - Image quality checks
   - Datasheet link validation (200 status codes)

OUTPUT FILES:
- tools/scrapers/abb_scraper.py (complete with error handling)
- tools/scrapers/sick_scraper.py
- tools/scrapers/siemens_scraper.py
- tools/scrapers/schneider_scraper.py
- tools/scrapers/murrelektronik_scraper.py
- tools/data_ingestion/csv_importer.py
- tools/data_ingestion/data_model.py (Pydantic models)
- tools/data_validation/validator.py
- tools/data_transformation/transformer.py
- tools/orchestration/scraper_schedule.py
- tools/orchestration/error_handler.py
- config/scraper_config.yaml
- config/field_mappings.yaml

QUALITY REQUIREMENTS:
- All scrapers must be resilient (retry logic, timeout handling)
- Support pagination across thousands of pages
- Rate limiting to respect manufacturer websites
- Comprehensive logging at every step
- Data quality metrics reported after each run
- No data loss (atomic transactions)
- Handles 100K+ products in <30 minutes

LANGUAGE: Python with type hints throughout. English documentation.
```

---

## PHASE 3: VECTOR DATABASE & EMBEDDING PIPELINE
### Goal: Index 100K+ products for semantic similarity search

**Prompt for Antigravity IDE:**

```
You are an AI/ML engineer specializing in semantic search and vector databases. 
Your task is to build a complete vector indexing pipeline for industrial automation 
product recommendation system.

REQUIREMENTS:

1. Create embedding pipeline:
   - Model: sentence-transformers/all-MiniLM-L6-v2 (free, 384-dim embeddings)
   - Input text: product_name + specifications + description + manufacturer + categories
   - Batch processing for 100K+ products (1000 embeddings/batch)
   - GPU acceleration if available, CPU fallback
   - Caching to avoid re-embedding identical products

2. Build Milvus vector database client:
   - Collection creation: "industrial_products" (768-dim, cosine similarity)
   - Metadata storage: sku_id, product_name, manufacturer, datasheet_url, images
   - Index configuration: IVF_FLAT for fast retrieval (<500ms for top-10)
   - Partition by manufacturer for faster filtering
   - Delete and update operations for product maintenance

3. Create indexing orchestration:
   - Connect to PostgreSQL to fetch all products
   - Generate embeddings in batches
   - Insert into Milvus with metadata
   - Progress tracking and resumable indexing
   - Validation: verify all products indexed
   - Health checks on vector DB

4. Build search interfaces:
   - similarity_search(query: str, k: int) → top-k products
   - search_by_specifications(specs: dict, k: int)
   - hybrid_search (combine vector + filters)
   - Advanced filters: manufacturer, industry, price range, certifications

5. Create re-indexing strategy:
   - Weekly incremental re-indexing
   - Batch delete old product versions
   - Add new products
   - Monitor index fragmentation
   - Optimize index if needed

6. Build monitoring & optimization:
   - Indexing time tracking
   - Search latency monitoring (<500ms target)
   - Cache hit rates
   - Index size tracking
   - Memory usage optimization

OUTPUT FILES:
- engine/embeddings/embedding_model.py (model initialization)
- engine/embeddings/vector_indexer.py (complete indexing pipeline)
- engine/embeddings/search_engine.py (search interfaces)
- engine/embeddings/cache.py (embedding cache)
- scripts/index_all_products.py (one-off indexing script)
- scripts/incremental_index.py (weekly update script)
- monitoring/embedding_metrics.py

QUALITY REQUIREMENTS:
- Index 100K products in <5 minutes
- Search latency <500ms for top-10
- Memory efficient (handle on 4GB RAM server)
- Graceful error handling
- Automatic recovery from failures
- Comprehensive logging

LANGUAGE: Python with numpy/torch. English documentation.
```

---

## PHASE 4: LLM & RAG (RETRIEVAL-AUGMENTED GENERATION) ENGINE
### Goal: Build AI recommendation core using Ollama + LangChain

**Prompt for Antigravity IDE:**

```
You are an expert LLM/AI Engineer specializing in Retrieval-Augmented Generation 
systems. Your task is to build the core recommendation engine.

REQUIREMENTS:

1. Ollama integration:
   - Download/manage Llama2-7B model
   - Model inference server at http://localhost:11434
   - Temperature: 0.2 (low randomness for factual recommendations)
   - Max tokens: 2000 (allow detailed responses)
   - Context window: 4096 tokens
   - Health monitoring and auto-restart

2. Build RAG chain with LangChain:
   - Vector store retriever (Milvus) with k=15
   - Prompt engineering for industrial automation
   - Context assembly (retrieved products → prompt)
   - Response parsing (JSON structure)
   - Citation generation (attach datasheet URLs)

3. Create recommendation prompt templates:
   
   Template A (Product Match):
   - Input: user query about industrial need
   - Output: single best-match product with reasoning
   - Include: SKU, name, confidence score, why it matches, datasheet link
   
   Template B (System Architecture):
   - Input: query requiring multiple products
   - Output: complete BOM with wiring, integration points
   - Include: products list, interconnection, cost estimate
   
   Template C (Troubleshooting):
   - Input: problem description
   - Output: diagnostic steps + recommended products for solution
   
   Template D (Alternatives):
   - Input: product currently using + constraints
   - Output: 3-5 alternatives ranked by relevance

4. Implement confidence scoring:
   - Vector similarity score (0-1)
   - Data completeness score
   - Manufacturer compatibility check
   - Final composite score (0.0-1.0)
   - Flag low-confidence recommendations (<0.6)

5. Build recommendation ranking:
   - Primary score: query-product semantic similarity
   - Secondary factors:
     * Product popularity (query frequency)
     * Availability in target country
     * Pricing competitiveness
     * User industry relevance
   - Reranking algorithm (BM25 + semantic)

6. Create complementary product suggestion:
   - Parse relationships from product data
   - Identify "often paired with" products
   - Suggest upsells (higher-priced alternatives)
   - Cross-sell recommendations

7. Build response formatting:
   - JSON structure with all recommendation details
   - Include source documents
   - Add explanation for technical terminology
   - Prepare for downstream multilingual translation

8. Error handling & fallbacks:
   - No products found → return "not found" with closest match
   - LLM failures → return raw retrieved products
   - Timeout handling (<5 second hard limit)
   - Partial response on interruption

OUTPUT FILES:
- engine/llm/model_config.py (Ollama + model setup)
- engine/llm/prompt_templates.py (all prompt variations)
- engine/rag/recommendation_chain.py (RAG orchestration)
- engine/rag/confidence_scorer.py (scoring logic)
- engine/rag/reranker.py (product reranking)
- engine/rag/complementary_products.py (upsell logic)
- engine/rag/response_formatter.py (JSON output formatting)
- scripts/test_rag_chain.py (testing script)

QUALITY REQUIREMENTS:
- Response time: <5 seconds end-to-end
- Accuracy: only recommend from indexed products (no hallucinations)
- Explainability: every recommendation includes reasoning
- Resilience: graceful degradation on LLM failures
- Accurate citations: every product linked to datasheet
- Confidence scores: calibrated and meaningful

LANGUAGE: Python with LangChain library. English documentation.
```

---

## PHASE 5: MULTIMODAL INPUT PROCESSING (Images/PDFs/Datasheets)
### Goal: Support image recognition, OCR, and PDF extraction for product matching

**Prompt for Antigravity IDE:**

```
You are a Computer Vision & Document Processing engineer. Your task is to build 
multimodal input processing for the recommendation system.

REQUIREMENTS:

1. Image processing pipeline:
   - Accept: product images (JPG, PNG, WebP)
   - OCR: extract visible text (Tesseract)
   - Vision: identify product type (BLIP model)
   - Generate: descriptive caption of what's shown
   - Combine: OCR text + visual understanding
   - Search: find matching products in database

2. PDF processing pipeline:
   - Accept: product datasheets, technical specs
   - Extract: text from all pages (PyPDF2)
   - Parse: structured data (model, specs, ratings, certifications)
   - OCR: handle scanned PDFs (if needed)
   - Index: searchable document content
   - Link: automatically find product in database

3. CSV/Excel sheet processing:
   - Accept: specification sheets
   - Parse: rows as product specs
   - Map: columns to product database fields
   - Find: exact product matches or close alternatives
   - Suggest: products matching the specifications

4. Build document similarity matching:
   - Convert document content → embedding
   - Search vector DB for similar products
   - Return ranked matches with confidence
   - Highlight why match was found

5. Create fallback matching:
   - If no perfect match: return closest alternatives
   - Explain differences from uploaded spec
   - Suggest customization or alternatives

6. Build upload handler:
   - File type validation
   - File size limits (max 50MB)
   - Virus scanning (optional)
   - Temporary file cleanup
   - Rate limiting (max 10 uploads/hour)

7. Create batch processing:
   - Handle multiple image uploads
   - Process in parallel (async)
   - Aggregate results
   - Return consolidated recommendations

OUTPUT FILES:
- engine/multimodal/document_processor.py (main orchestrator)
- engine/multimodal/ocr_engine.py (Tesseract wrapper)
- engine/multimodal/image_recognizer.py (BLIP vision model)
- engine/multimodal/pdf_extractor.py (PDF parsing)
- engine/multimodal/sheet_parser.py (CSV/Excel)
- engine/multimodal/document_matcher.py (similarity matching)
- api/upload_handler.py (FastAPI upload endpoint)
- scripts/test_multimodal.py

QUALITY REQUIREMENTS:
- Image processing: <2 seconds per image
- PDF extraction: <3 seconds per document
- Accurate OCR: >95% for clear text
- Robust error handling (corrupted files, unsupported formats)
- GDPR compliant (delete uploads after processing)
- Support multiple document languages (English + Arabic)

LANGUAGE: Python with OpenCV, Tesseract, PyPDF2, Hugging Face Transformers.
```

---

## PHASE 6: WEB API & WOOCOMMERCE INTEGRATION
### Goal: Build FastAPI server and integrate with WooCommerce

**Prompt for Antigravity IDE:**

```
You are a Full-Stack API & E-commerce Integration engineer. Your task is to build 
the REST API and WooCommerce integration layer.

REQUIREMENTS:

1. FastAPI server architecture:
   - Port: 8000 (internal communication)
   - CORS: allow alsakronline.com domain
   - Request logging: all queries logged
   - Rate limiting: prevent abuse (100 queries/minute per IP)
   - Error handling: standardized JSON error responses
   - Health check endpoint: /api/v1/health

2. Core API endpoints:

   POST /api/v1/recommend
   - Input: {query: str, language: "en"|"ar", user_id?: str, session_id?: str}
   - Output: {status, primary_recommendation, alternatives, confidence_score, sources}
   - Latency: <5 seconds
   - Logging: log all queries for analytics
   
   POST /api/v1/upload-document
   - Input: multipart file upload (image/pdf/sheet)
   - Output: {status, matched_products, confidence_scores}
   - Support: JPG, PNG, PDF, CSV, Excel
   
   POST /api/v1/contact-capture
   - Input: {name, email, company, phone, industry, country}
   - Output: {status, contact_id}
   - Trigger: CRM workflow (n8n)
   
   POST /api/v1/quotation-request
   - Input: {sku_ids, quantities, delivery_country, contact}
   - Output: {status, quotation_id}
   - Action: send to sales team + trigger n8n workflow
   
   GET /api/v1/product/{sku_id}
   - Return: complete product details, alternatives, related products
   
   WebSocket /ws/chat/{session_id}
   - Real-time chat with recommendations
   - Support: streaming responses
   - Keep-alive: 30-minute timeout

3. Authentication & Authorization:
   - API key for WooCommerce plugin
   - Session-based for web chat
   - User tracking (anonymous + registered)

4. Input validation:
   - Pydantic models for all endpoints
   - Query length: max 1000 characters
   - File uploads: max 50MB
   - Rate limiting per IP

5. Response formatting:
   - Standardized JSON structure
   - Include metadata: timestamp, request_id
   - Compress large responses (gzip)
   - Include correlation IDs for debugging

6. Logging & monitoring:
   - Structured JSON logging
   - Error tracking (stack traces)
   - Performance metrics (latency, throughput)
   - User interaction tracking

7. WooCommerce plugin integration:
   - PHP plugin that injects chat widget
   - Widget: fixed position (bottom-right)
   - Languages: English + Arabic toggle
   - Features:
     * Real-time chat
     * Product suggestions shown in widget
     * "Add to cart" button integration
     * "Request quotation" form
     * Upload document support
   - Styling: match WooCommerce theme

8. Product sync mechanism:
   - WooCommerce → Recommendation Engine
   - Trigger: on product update/publish
   - Sync: SKU, name, price, description, images, categories
   - Two-way: recommendation engine can update WC product links

OUTPUT FILES:
- api/server.py (FastAPI main app - 500+ lines)
- api/routes/recommendations.py (recommend endpoint)
- api/routes/documents.py (upload endpoint)
- api/routes/contacts.py (contact capture)
- api/routes/quotations.py (quotation requests)
- api/models/schemas.py (Pydantic models)
- api/middleware/auth.py (authentication)
- api/middleware/logging.py (request logging)
- api/websocket/chat_handler.py (WebSocket chat)
- wp-content/plugins/industrial-recommendation-engine/plugin.php (500+ lines)
- wp-content/plugins/industrial-recommendation-engine/assets/widget.js
- wp-content/plugins/industrial-recommendation-engine/assets/widget.css
- scripts/test_api_endpoints.py (comprehensive tests)

QUALITY REQUIREMENTS:
- 99.9% uptime target
- <5 second response time (p95)
- Concurrent users: support 100+ simultaneous connections
- Graceful degradation on failures
- HTTPS only (TLS 1.2+)
- Input validation on all endpoints
- Security: CSRF protection, SQL injection prevention

LANGUAGE: Python (FastAPI) and PHP (WordPress plugin).
```

---

## PHASE 7: PURCHASING JOURNEY & CRM AUTOMATION
### Goal: Implement lead capture, quotation management, and n8n workflows

**Prompt for Antigravity IDE:**

```
You are a CRM specialist and workflow automation engineer. Your task is to build 
the purchasing journey and integrate with n8n for marketing automation.

REQUIREMENTS:

1. Lead capture flow:
   - Contact form: collect name, email, company, phone, industry, country
   - Validation: email format, required fields
   - CRM storage: save to PostgreSQL
   - Duplicate detection: check for existing contact
   - Trigger: n8n workflow for lead qualification

2. Lead qualification workflow (n8n):
   - Input: new contact → n8n webhook
   - Logic:
     * Check industry: route to appropriate sales team
     * Check country: assign regional sales rep
     * Check company size: adjust approach (enterprise vs SMB)
   - Actions:
     * Send welcome email
     * Create HubSpot/Salesforce contact
     * Add to email nurture sequence
     * Notify sales team

3. Quotation management:
   - Capture: selected products + quantities
   - Calculate: total price based on manufacturing data
   - Generate: professional quotation PDF
   - Store: in database with expiry (30 days)
   - Send: to customer + sales team
   - Track: quotation status (sent, viewed, accepted, expired)

4. Purchasing journey stages:

   Stage 1: Discovery
   - Recommendation query
   - Browse products
   - View datasheets
   - Comparison shopping
   
   Stage 2: Engagement
   - Add items to cart
   - Request quotation
   - Upload specifications
   - Ask questions (chat)
   
   Stage 3: Contact Capture
   - Collect contact details
   - Capture use case
   - Document industry requirements
   
   Stage 4: Quotation
   - Generate formal quote
   - Include alternatives
   - Show delivery timeline
   - Highlight certifications/compliance
   
   Stage 5: Upselling
   - Suggest complementary products
   - Show volume discounts
   - Recommend related categories
   - Cross-sell related products
   
   Stage 6: Conversion
   - Direct purchase (if price < threshold)
   - Quotation approval (if price > threshold)
   - Order confirmation
   - Next steps (delivery, integration)

5. Upselling engine:
   - Get primary recommendation → SKU
   - Query: "often_paired_with" relationships
   - Get: complementary products
   - Rank: by relevance + margin
   - Suggest: top 3-5 upsells
   - Format: as "frequently purchased together"

6. Quotation PDF generator:
   - Template: professional branding (Alsakronline logo)
   - Content:
     * Quote ID, date, expiry
     * Customer info
     * Product list: SKU, name, qty, unit price, total
     * Subtotal, tax, shipping, grand total
     * Terms & conditions
     * Contact info + sales rep
   - Library: ReportLab or similar
   - Output: save to DB + email to customer

7. Email integration:
   - Welcome email: "thanks for your interest"
   - Quotation email: "your quote is ready"
   - Follow-up emails: abandoned cart after 2 days
   - Confirmation email: "order confirmed"
   - Tracking: email open rates, click rates

8. Analytics & reporting:
   - Funnel tracking: discovery → quotation → purchase
   - Conversion rate by industry/country
   - Average order value by recommendation type
   - Time-to-purchase
   - Upsell attachment rate

OUTPUT FILES:
- engine/purchasing/journey_handler.py (main orchestrator)
- engine/purchasing/lead_capture.py (contact management)
- engine/purchasing/quotation_generator.py (quote creation)
- engine/purchasing/pdf_generator.py (PDF quotation)
- engine/purchasing/upsell_engine.py (complementary products)
- engine/purchasing/analytics.py (funnel tracking)
- n8n/workflows/lead_qualification.json (workflow definition)
- n8n/workflows/quotation_pipeline.json
- email_templates/welcome.html
- email_templates/quotation.html
- email_templates/follow_up.html
- scripts/test_journey.py

QUALITY REQUIREMENTS:
- Lead capture: all fields validated
- CRM sync: real-time to external systems
- Quotation PDF: professional appearance, <1 second generation
- Email delivery: 99.9% success rate
- Funnel tracking: accurate and real-time
- GDPR compliant: consent capture, easy unsubscribe

LANGUAGE: Python (backend) + HTML/CSS (email templates) + n8n JSON workflows.
```

---

## PHASE 8: MULTILINGUAL SUPPORT (ENGLISH + ARABIC)
### Goal: Full localization for English and Arabic users

**Prompt for Antigravity IDE:**

```
You are a Localization & NLP engineer. Your task is to build comprehensive 
multilingual support for English and Arabic.

REQUIREMENTS:

1. Language detection:
   - Auto-detect query language
   - Support: English (en) + Arabic (ar)
   - Fallback: English if uncertain
   - Store: user language preference

2. Translation pipeline:
   - English ↔ Arabic machine translation
   - Model: Helsinki-NLP/opus-mt-en-ar (free)
   - Cached translations (avoid re-translating)
   - Quality check: >0.95 translation confidence

3. Prompt localization:
   - Maintain system prompt in English
   - Translate retrieval context to user language
   - Generate response in user language
   - Use language-specific terminology

4. Tone & cultural adaptation:
   - English: technical, direct, efficiency-focused
   - Arabic: formal, respectful, detailed
   - Industry terminology: localized for both languages
   - Certifications: use local standard names (CE → CE/ATEX, etc.)

5. Right-to-left (RTL) support:
   - UI: Arabic text displays RTL
   - CSS: flex-direction changes for RTL
   - Forms: field layout adjusted
   - Chat: message alignment for RTL

6. Local context customization:
   - Arabic: emphasize suppliers in Middle East/Egypt
   - English: global suppliers available
   - Pricing: show in local currency (USD, EGP, AED)
   - Delivery: show estimates for target country
   - Compliance: show relevant certifications

7. Documentation translation:
   - Help text: both languages
   - FAQ: both languages
   - Product descriptions: both languages
   - Error messages: localized

OUTPUT FILES:
- engine/translation/translator.py (translation engine)
- engine/translation/language_detector.py (language detection)
- engine/translation/prompt_localizer.py (prompt translation)
- engine/translation/tone_adapter.py (tone adjustment)
- config/language_config.yaml (localization settings)
- templates/ui_strings.json (all UI text, both languages)
- frontend/assets/styles_rtl.css (RTL styles)
- scripts/translate_database.py (batch translate products)

QUALITY REQUIREMENTS:
- Translation latency: <1 second
- Translation quality: >0.9 BLEU score
- UI responsiveness: no layout shifts for RTL
- Culturally appropriate: no offensive translations
- Terminology consistency: same terms used throughout
- Support for both languages seamlessly

LANGUAGE: Python with transformers library + CSS for RTL.
```

---

## PHASE 9: MONITORING, TESTING & DEPLOYMENT
### Goal: Build comprehensive monitoring, testing, and production deployment

**Prompt for Antigravity IDE:**

```
You are a DevOps & QA Engineer. Your task is to build monitoring, testing, 
and production deployment infrastructure.

REQUIREMENTS:

1. Testing framework:
   - Unit tests: all Python modules (pytest)
   - Integration tests: API endpoints
   - Load tests: 100+ concurrent users
   - End-to-end tests: full recommendation flow
   - Target: >90% code coverage

2. Performance testing:
   - Load test: 1000 recommendations/hour
   - Latency test: <5 second p95
   - Concurrency test: 50+ simultaneous users
   - Vector search performance: <500ms for top-10

3. Monitoring stack:
   - Prometheus: metrics collection
   - Grafana: dashboards & visualization
   - Application logging: structured JSON logs
   - Error tracking: Sentry or similar
   - Uptime monitoring: external health checks

4. Key metrics to track:
   - Recommendation latency (p50, p95, p99)
   - Vector search latency
   - API response times per endpoint
   - Error rates by type
   - Database query times
   - Cache hit rates
   - Active users
   - Recommendation confidence distribution

5. Alerting rules:
   - Alert if latency > 5 seconds
   - Alert if error rate > 1%
   - Alert if disk space < 10%
   - Alert if memory usage > 80%
   - Alert if API downtime > 5 minutes

6. Deployment process:
   - Build: Docker image
   - Test: automated tests on staging
   - Deploy: to production (blue-green)
   - Verification: health checks
   - Rollback: automatic if health checks fail

7. Production deployment:
   - Setup: Hostinger Business Web Hosting
   - Containerization: Docker + docker-compose
   - Orchestration: docker-compose (single server)
   - Reverse proxy: Nginx for SSL/TLS
   - Database backups: daily automated backups
   - Log retention: 30-day rolling logs

8. Security hardening:
   - HTTPS/TLS: all traffic encrypted
   - Secrets management: environment variables
   - API keys: rotate quarterly
   - Database passwords: strong, unique
   - Firewall: limit to necessary ports
   - GDPR: data retention policies

OUTPUT FILES:
- tests/test_api_endpoints.py (API tests)
- tests/test_rag_chain.py (RAG logic tests)
- tests/test_vector_search.py (search tests)
- tests/test_data_pipeline.py (ETL tests)
- tests/load_test.py (performance testing - Locust)
- monitoring/prometheus_config.yml
- monitoring/grafana_dashboards.json
- monitoring/alert_rules.yml
- deployment/docker-compose.prod.yml
- deployment/nginx.conf (reverse proxy)
- deployment/deploy.sh (deployment script)
- deployment/backup.sh (database backup)
- deployment/monitoring.sh (monitoring setup)
- scripts/health_check.py
- README_DEPLOYMENT.md

QUALITY REQUIREMENTS:
- >90% test coverage
- All tests pass before deployment
- <5 second latency for 95th percentile
- <1% error rate in production
- 99.9% uptime target
- All alerts actionable and tested
- Automated rollback on failures

LANGUAGE: Python (tests) + YAML (configs) + Bash (scripts) + Nginx (config).
```

---

## FINAL INTEGRATION & HANDOFF
### Goal: Complete system integration and production launch

**Prompt for Antigravity IDE:**

```
You are a Principal Systems Engineer. Your task is to orchestrate the final 
integration and coordinate production launch.

REQUIREMENTS:

1. Pre-launch checklist:
   ✓ All 9 phases complete and tested
   ✓ 100K products indexed and searchable
   ✓ Recommendation accuracy validated (>85%)
   ✓ Latency validated (<5 seconds p95)
   ✓ GDPR compliance verified
   ✓ Security audit completed
   ✓ Load testing passed (1000 QPS)
   ✓ Monitoring and alerting active
   ✓ Backup and recovery tested
   ✓ Team trained on operations

2. Production deployment:
   - Schedule: deploy outside business hours
   - Staging validation: test on staging first
   - Database migration: zero-downtime strategy
   - Health monitoring: intensive during first 24 hours
   - Rollback plan: documented and rehearsed

3. Go-live support:
   - On-call engineer: 24/7 for 1 week
   - Issue resolution: SLA <30 minutes
   - User feedback: collect and triage
   - Performance monitoring: continuous

4. Post-launch optimization:
   - Week 1: stabilize, fix critical bugs
   - Week 2: performance tuning
   - Week 3: feature enhancement
   - Week 4: scale if needed

5. Handoff documentation:
   - Operations runbook
   - Troubleshooting guide
   - API documentation (Swagger/OpenAPI)
   - System architecture diagram
   - Database schema documentation
   - Contact escalation procedures

OUTPUT FILES:
- DEPLOYMENT_CHECKLIST.md
- OPERATIONS_RUNBOOK.md
- TROUBLESHOOTING_GUIDE.md
- API_DOCUMENTATION.md (OpenAPI spec)
- ARCHITECTURE_DIAGRAM.md
- DATABASE_SCHEMA_DOCS.md
- TEAM_TRAINING_GUIDE.md
- INCIDENT_RESPONSE_PROCEDURES.md
- SCALING_GUIDE.md

QUALITY REQUIREMENTS:
- Production systems operating without issues
- Team confident to operate independently
- Clear documentation for future reference
- Proven incident response procedures
- Path for future enhancements

LANGUAGE: Markdown documentation + YAML configs.
```

---

## EXECUTION TIMELINE

| Phase | Week | Duration | Status | Key Deliverables |
|-------|------|----------|--------|------------------|
| 1 | W1 | 2 days | Foundation | Docker, PostgreSQL, Milvus, Ollama ready |
| 2 | W1 | 2 days | Data Ingestion | 50K products scraped & validated |
| 3 | W1 | 1 day | Embedding | All products indexed in Milvus |
| 4 | W2 | 1 day | RAG Engine | LLM + recommendation chain working |
| 5 | W2 | 1 day | Multimodal | Image/PDF upload & matching working |
| 6 | W2 | 2 days | API & Integration | FastAPI server + WooCommerce widget live |
| 7 | W3 | 2 days | Purchasing | Lead capture + quotation pipeline live |
| 8 | W3 | 1 day | Multilingual | English + Arabic fully working |
| 9 | W3-W4 | 2 days | Monitoring & Deploy | Production deployment + monitoring active |
| - | W4 | - | Production | Live on alsakronline.com |

---

## SUCCESS CRITERIA

- ✅ MVP: All core features working by Day 7
- ✅ Accuracy: Recommendations >85% relevant (user feedback)
- ✅ Speed: <5 second response time (p95)
- ✅ Scale: Handle 100K+ SKUs
- ✅ Reliability: 99.9% uptime
- ✅ Language: Both English and Arabic fully functional
- ✅ Integration: Seamlessly integrated with WooCommerce
- ✅ Security: GDPR compliant, encrypted, secure
- ✅ Monitoring: Complete observability + alerting
- ✅ Usability: Intuitive UI, clear documentation

---

**End of Antigravity IDE Multi-Phase Prompt**

This prompt is designed to be fed into Antigravity IDE or Claude AI IDE phase-by-phase.
Each phase can be executed sequentially, with outputs from each phase feeding into the next.
