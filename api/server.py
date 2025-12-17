from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import os
from prometheus_fastapi_instrumentator import Instrumentator

from api.routes import recommendations, documents, contacts, quotations, auth, chat

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Industrial Automation AI Engine",
    description="RAG-based recommendation engine for SICK, ABB, Siemens products.",
    version="1.0.0"
)

# Instrumentation
Instrumentator().instrument(app).expose(app)

# CORS Middleware (Allow all for development, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(documents.router, prefix="/api/v1", tags=["Documents"])
app.include_router(contacts.router, prefix="/api/v1", tags=["Contacts"])
app.include_router(quotations.router, prefix="/api/v1", tags=["Quotations"])

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/")
def root():
    return {"message": "Industrial Automation AI API is running. Go to /docs for Swagger UI."}

