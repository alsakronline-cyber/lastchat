from engine.rag.recommendation_chain import RecommendationChain
from engine.rag.confidence_scorer import ConfidenceScorer

# Lazy singleton instances
_chain = None
_scorer = None

def get_rag_chain():
    global _chain
    if _chain is None:
        _chain = RecommendationChain()
    return _chain

def get_confidence_scorer():
    global _scorer
    if _scorer is None:
        _scorer = ConfidenceScorer()
    return _scorer
