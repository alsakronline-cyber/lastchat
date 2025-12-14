# Deploy files individually
docker_compose_content=$(cat <<EOF
version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: automation-postgres
    restart: unless-stopped
    ports: ["5432:5432"]
    environment:
      POSTGRES_USER: \${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD:-secure_password}
      POSTGRES_DB: \${POSTGRES_DB:-automation_engine}
    volumes: [postgres_data:/var/lib/postgresql/data]
    networks: [automation-net]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  milvus:
    image: milvusdb/milvus:v2.3.0
    container_name: automation-milvus
    restart: unless-stopped
    command: ["milvus", "run", "standalone"]
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
    volumes: [milvus_data:/var/lib/milvus]
    ports: ["19530:19530", "9091:9091"]
    networks: [automation-net]
    depends_on: ["etcd", "minio"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9091/healthz"]
      interval: 30s
      timeout: 20s
      retries: 3

  etcd:
    image: quay.io/coreos/etcd:v3.5.0
    container_name: automation-etcd
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
      - ETCD_SNAPSHOT_COUNT=50000
    volumes: [etcd_data:/etcd]
    command: etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    networks: [automation-net]

  minio:
    image: minio/minio:RELEASE.2023-03-20T20-16-18Z
    container_name: automation-minio
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    ports: ["9001:9001", "9000:9000"]
    volumes: [minio_data:/minio_data]
    command: minio server /minio_data --console-address ":9001"
    networks: [automation-net]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: automation-redis
    restart: unless-stopped
    ports: ["6379:6379"]
    volumes: [redis_data:/data]
    networks: [automation-net]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  ollama:
    image: ollama/ollama:latest
    container_name: automation-ollama
    restart: unless-stopped
    ports: ["11434:11434"]
    volumes: [ollama_models:/root/.ollama]
    networks: [automation-net]

  api:
    build: .
    container_name: automation-engine
    restart: unless-stopped
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://postgres:secure_password@postgres:5432/automation_engine
      - MILVUS_HOST=milvus
      - MILVUS_PORT=19530
      - REDIS_URL=redis://redis:6379/0
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes: [.:/app]
    depends_on:
      postgres: {condition: service_healthy}
      milvus: {condition: service_healthy}
      redis: {condition: service_healthy}
    networks: [automation-net]
    command: uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

networks:
  automation-net:
    driver: bridge

volumes:
  postgres_data:
  milvus_data:
  etcd_data:
  minio_data:
  redis_data:
  ollama_models:
EOF
)
echo "$docker_compose_content" > docker-compose.yml

dockerfile_content=$(cat <<EOF
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client tesseract-ocr libsm6 libxext6 libgl1-mesa-glx curl build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8000/api/v1/health || exit 1
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
)
echo "$dockerfile_content" > Dockerfile

requirements_content=$(cat <<EOF
fastapi==0.109.2
uvicorn==0.27.1
pydantic==2.6.1
pydantic-settings==2.1.0
python-multipart==0.0.9
psycopg2-binary==2.9.9
sqlalchemy==2.0.27
alembic==1.13.1
pymilvus==2.3.6
redis==5.0.1
langchain==0.1.7
langchain-community==0.0.20
langchain-core==0.1.23
sentence-transformers==2.3.1
transformers==4.37.2
torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu
pillow==10.2.0
pytesseract==0.3.10
pypdf2==3.0.1
pandas==2.2.0
openpyxl==3.1.2
scrapy==2.11.0
selenium==4.17.2
beautifulsoup4==4.12.3
requests==2.31.0
prometheus-fastapi-instrumentator==6.1.0
EOF
)
echo "$requirements_content" > requirements.txt

env_content=$(cat <<EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=automation_engine
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
MILVUS_HOST=milvus
MILVUS_PORT=19530
REDIS_URL=redis://redis:6379/0
OLLAMA_BASE_URL=http://ollama:11434
MODEL_NAME=llama2:7b
SECRET_KEY=change_this_to_a_secure_random_string_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1
PROJECT_NAME="Industrial Automation Recommendation Engine"
EOF
)
echo "$env_content" > .env

mkdir -p alembic/versions
touch alembic/env.py
touch alembic.ini
