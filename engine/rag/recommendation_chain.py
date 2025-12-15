import logging
from typing import Dict, List, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from engine.llm.model_config import get_model
from engine.llm.prompt_templates import get_rag_prompt, format_docs
from engine.embeddings.search_engine import SearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationChain:
    """
    Core RAG engine that combines retrieval (Vector DB) and generation (LLM)
    to provide product recommendations.
    """
    
    def __init__(self):
        self.llm = get_model()
        self.search_engine = SearchEngine()
        self.prompt = get_rag_prompt()
        self.output_parser = StrOutputParser()
        
        # Define the chain
        # 1. 'context' comes from the retriever (SearchEngine)
        # 2. 'question' is passed through
        # 3. Prompt formats inputs
        # 4. LLM generates answer
        self.chain = (
            {"context": lambda x: format_docs(x["context"]), "question": lambda x: x["question"]}
            | self.prompt
            | self.llm
            | self.output_parser
        )

    def get_recommendation(self, user_query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Processes a user query and returns a recommendation.
        
        Args:
            user_query (str): The user's technical question.
            top_k (int): Number of products to retrieve for context.
            
        Returns:
            Dict: {
                "answer": str (LLM response),
                "source_documents": List[Dict] (The products found)
            }
        """
        logger.info(f"Processing RAG query: {user_query}")
        
        # 1. Retrieve Context
        try:
            retrieved_products = self.search_engine.search_products(user_query, limit=top_k)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {"answer": "I encountered an error searching for products.", "source_documents": []}
        
        # 2. Generate Answer
        try:
            # We invoke the chain manually to control the context injection clearly
            input_data = {
                "context": retrieved_products,
                "question": user_query
            }
            
            answer = self.chain.invoke(input_data)
            
            return {
                "answer": answer,
                "source_documents": retrieved_products
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "answer": "I found some products but failed to generate a recommendation description.",
                "source_documents": retrieved_products
            }

if __name__ == "__main__":
    # Simple test
    try:
        rag = RecommendationChain()
        result = rag.get_recommendation("I need a high precision laser distance sensor")
        print("\n--- Recommendation ---")
        print(result["answer"])
        print("\n--- Sources ---")
        for p in result["source_documents"]:
            print(f"- {p.get('name')} ({p.get('sku')})")
            
    except Exception as e:
        print(f"Test failed: {e}")
