import logging
from typing import Dict, List, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from engine.translation.language_detector import LanguageDetector
from engine.translation.translator import AutoTranslator

from engine.llm.model_config import get_model
from engine.llm.prompt_templates import get_rag_prompt, format_docs
from engine.embeddings.search_engine import SearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationChain:
    """
    Core RAG engine that combines retrieval (Vector DB) and generation (LLM)
    to provide product recommendations. Supports Multilingual (Ar/En).
    """
    
    def __init__(self):
        self.llm = get_model()
        self.search_engine = SearchEngine()
        self.prompt = get_rag_prompt()
        self.output_parser = StrOutputParser()
        
        # Translation components
        self.detector = LanguageDetector()
        self.translator = AutoTranslator()
        
        # Define the chain
        self.chain = (
            {"context": lambda x: format_docs(x["context"]), "question": lambda x: x["question"]}
            | self.prompt
            | self.llm
            | self.output_parser
        )

    def get_recommendation(self, user_query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Processes a user query (auto-translates if Arabic) and returns a recommendation.
        """
        logger.info(f"Processing RAG query: {user_query}")
        
        # 0. Language Detection & Translation
        lang = self.detector.detect_language(user_query)
        logger.info(f"Detected language: {lang}")
        
        query_to_search = user_query
        if lang == 'ar':
            query_to_search = self.translator.translate_to_english(user_query)
            logger.info(f"Translated query: {query_to_search}")

        # 1. Retrieve Context
        try:
            retrieved_products = self.search_engine.search_products(query_to_search, limit=top_k)
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {"answer": "I encountered an error searching for products." if lang == 'en' else "حدث خطأ أثناء البحث عن المنتجات.", "source_documents": [], "detected_language": lang}
        
        # 1.1 Short-circuit if no products found (Prevent Hallucinations)
        if not retrieved_products:
            logger.info("No products found in vector DB. Short-circuiting LLM.")
            no_match_msg = "I could not find any matching products in the database."
            if lang == 'ar':
                no_match_msg = "لم أتمكن من العثور على أي منتجات مطابقة في قاعدة البيانات."
            
            return {
                "answer": no_match_msg,
                "source_documents": [],
                "detected_language": lang
            }

        # 2. Generate Answer
        try:
            # We invoke the chain manually to control the context injection clearly
            input_data = {
                "context": retrieved_products,
                "question": query_to_search # LLM sees English query + English context
            }
            
            # This generates English answer
            answer_en = self.chain.invoke(input_data)
            
            # 3. Translate Answer back if needed
            final_answer = answer_en
            if lang == 'ar':
                final_answer = self.translator.translate_to_arabic(answer_en)

            return {
                "answer": final_answer,
                "source_documents": retrieved_products,
                "detected_language": lang
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            fallback = "I found some products but failed to generate a recommendation."
            if lang == 'ar':
                fallback = "وجدت بعض المنتجات ولكن فشلت في تقديم توصية."
                
            return {
                "answer": fallback,
                "source_documents": retrieved_products,
                "detected_language": lang
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
