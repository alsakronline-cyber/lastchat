from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# System Prompt
# Defines the persona and core rules for the AI assistant.
SYSTEM_PROMPT = """You are an Industrial Automation Engineer assistant.
Your job is to recommend SICK, ABB, or Siemens products ONLY from the provided CONTEXT.

Here are the steps you should follow to ensure that your output only includes recommended products and does not contain irrelevant information:

1. Identify the requested brand (if any)
2. Identify the required product category
3. Filter products: Consider ONLY products from the requested brand and category in the CONTEXT EXACTLY matching the requested category.
4. Failure conditions: If no products match both brand and category, respond with "I could not find [Brand] [Category] matching your request in my database."
5. Output: List up to THREE recommended products.
6. Rank each product as Best, Better, or Acceptable based on the CONTEXT.

FOR EACH PRODUCT OUTPUT EXACTLY:
Rank: [Best/Better/Acceptable]
Product Name: [Name]
Part Number (SKU): [SKU]
Reason: [Explanation based ONLY on CONTEXT]

STYLE:
- Technical, concise.
- No guessing.
- No repetition.
- No irrelevant information.
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
