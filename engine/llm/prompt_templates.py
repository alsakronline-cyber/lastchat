from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# System Prompt
# Defines the persona and core rules for the AI assistant.
SYSTEM_PROMPT = """You are an expert Industrial Automation Engineer assistant. 
Your goal is to recommend the best SICK, ABB, or Siemens products based on the user's technical requirements.

RULES:
1. ONLY recommend products found in the provided CONTEXT.
2. If the Context is empty or irrelevant, strictly state: "I could not find specific products matching your requirements in my database."
3. Do not invent products or part numbers. Hallucination is strictly forbidden.
4. Always provide the "Part Number" (SKU) and "Product Name" for every recommendation.
5. Explain WHY you selected a product based on its technical specifications.
6. If multiple options exist, briefly compare them (e.g., cable length, switching distance).
7. Be concise and professional.
"""

# RAG Prompt Template
# Variables: {context} (retrieved products), {question} (user query)
RAG_TEMPLATE_STR = """
{system_prompt}

CONTEXT (Found Products):
{context}

USER QUESTION: 
{question}

ENGINEER RECOMMENDATION:
"""

def get_rag_prompt():
    """Returns the ChatPromptTemplate for the RAG chain."""
    return ChatPromptTemplate.from_template(
        RAG_TEMPLATE_STR, 
        partial_variables={"system_prompt": SYSTEM_PROMPT}
    )

def format_docs(docs):
    """
    Format retrieved documents (Milvus hits) into a string for the prompt.
    Expecting 'docs' to be a list of dicts (from SearchEngine).
    """
    formatted_context = ""
    for i, doc in enumerate(docs):
        # Handle both LangChain Document objects and our raw Dicts from SearchEngine
        if hasattr(doc, 'page_content'):
            content = doc.page_content
            metadata = doc.metadata
        else:
             # It's our dict from SearchEngine
             content = f"Product: {doc.get('name')} | SKU: {doc.get('sku')} | Category: {doc.get('category')}"
             metadata = doc # Or doc.get('metadata', {})
        
        formatted_context += f"{i+1}. {content}\n"
        
    return formatted_context or "No relevant products found."
