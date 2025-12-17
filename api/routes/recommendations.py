from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from engine.rag.recommendation_chain import RecommendationChain
from engine.rag.confidence_scorer import ConfidenceScorer

router = APIRouter()
logger = logging.getLogger(__name__)

# Request Model
class RecommendationRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

# Response Model
class ProductSource(BaseModel):
    name: str
    sku: str
    category: Optional[str] = None
    score: Optional[float] = None

class RecommendationResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[ProductSource]

from api.dependencies import get_rag_chain, get_confidence_scorer

@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendation(request: RecommendationRequest):
    """
    Get AI-powered product recommendations based on technical requirements.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"API Recommendation Request: {request.query}")
    
    try:
        chain = get_rag_chain()
        scorer = get_confidence_scorer()
        
        # Run RAG
        result = chain.get_recommendation(request.query, top_k=request.top_k)
        
        # Calculate Confidence
        confidence = scorer.calculate_score(request.query, result["source_documents"])
        
        # Format Sources
        sources = []
        for doc in result["source_documents"]:
            sources.append(ProductSource(
                name=doc.get("name", "Unknown"),
                sku=doc.get("sku", "Unknown"),
                category=doc.get("category"),
                score=doc.get("score")
            ))
            
        return RecommendationResponse(
            answer=result["answer"],
            confidence=confidence,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
