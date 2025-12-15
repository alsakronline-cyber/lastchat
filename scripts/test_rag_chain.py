import sys
import os
import logging
import argparse

# Add project root to sys.path
sys.path.append(os.getcwd())

from engine.rag.recommendation_chain import RecommendationChain
from engine.rag.confidence_scorer import ConfidenceScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag(query: str):
    print(f"\n🚀 Starting RAG Test for query: '{query}'")
    
    try:
        # 1. Init Chain
        chain = RecommendationChain()
        scorer = ConfidenceScorer()
        
        # 2. Run
        print("🔍 Searching and Generating...")
        result = chain.get_recommendation(query)
        
        # 3. Calculate Confidence
        confidence = scorer.calculate_score(query, result["source_documents"])
        
        # 4. Display Results
        print("\n" + "="*50)
        print(f"🤖 AI RECOMMENDATION (Confidence: {confidence})")
        print("="*50)
        print(result["answer"])
        print("\n" + "-"*50)
        print(f"📚 SOURCE DOCUMENTS ({len(result['source_documents'])})")
        print("-"*50)
        for i, doc in enumerate(result["source_documents"]):
            print(f"[{i+1}] {doc.get('name')} (SKU: {doc.get('sku')}) - Score: {doc.get('score'):.4f}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        # Print stack trace
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the RAG Chain")
    parser.add_argument("query", nargs="?", default="I need a photoelectric sensor for detecting transparent objects", help="Query to test")
    args = parser.parse_args()
    
    test_rag(args.query)
