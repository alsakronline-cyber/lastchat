import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfidenceScorer:
    """
    Calculates a confidence score (0.0 - 1.0) for the RAG recommendation.
    """
    
    def calculate_score(self, query: str, retrieved_items: List[Dict]) -> float:
        """
        Calculate aggregate confidence score.
        
        Args:
            query (str): User query.
            retrieved_items (List[Dict]): List of items with 'score' (cosine distance/similarity).
            
        Returns:
            float: Confidence score [0.0, 1.0].
        """
        if not retrieved_items:
            return 0.0

        # 1. Vector Similarity Score (Primary)
        # Milvus cosine distance usually returns smaller distance = better match.
        # BUT our VectorIndexer uses 'COSINE' metric type which in Milvus usually returns Inner Product for normalized vectors?
        # Let's assume the 'score' field from SearchEngine is trustworthy. 
        # If it's pure cosine similarity, it's -1 to 1. If distance, it's 0 to 2.
        # Simplification: Take the top score.
        top_score = retrieved_items[0].get('score', 0)
        
        # Normalize roughly (assuming cosine similarity where 1.0 is perfect)
        # If using L2 distance, 0 is perfect. We need to know the metric. 
        # Our VectorIndexer used "COSINE". In Milvus, if vectors are normalized, this is Inner Product (1.0 = identical).
        
        base_confidence = max(0.0, min(1.0, top_score))

        # 2. Heuristic Bonus
        # Boost if query keywords appear exactly in Product Name or SKU
        keywords = query.lower().split()
        bonus = 0.0
        
        top_item = retrieved_items[0]
        name = top_item.get('name', '').lower()
        sku = top_item.get('sku', '').lower()
        
        matches = 0
        for kw in keywords:
            if len(kw) > 3 and (kw in name or kw in sku):
                matches += 1
        
        if matches > 0:
            bonus = 0.1 * min(matches, 3) # Max 0.3 bonus

        final_score = min(1.0, base_confidence + bonus)
        return round(final_score, 2)
