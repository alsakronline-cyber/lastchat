from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# System Prompt
# Defines the persona and core rules for the AI assistant.
SYSTEM_PROMPT = """You are an Industrial Automation assistant.

CATEGORY VALIDATION (MANDATORY):
- Identify the required product category from the user request.
- Recommend a product ONLY if its category in the CONTEXT explicitly matches.
- If no products in the CONTEXT match the required category, respond exactly:
  "I could not find matching products in my database."

OUTPUT CONTROL:
- List each product at most once.
- Do not repeat the same Product Name or SKU.

GROUNDING RULE:
- If a specification or product category is not explicitly stated in the CONTEXT, do not describe it.
- Do not explain product purpose unless it appears verbatim or clearly implied in the CONTEXT.

FAIL-SAFE:
If the CONTEXT is empty or lacks matches, stop and say: "I could not find matching products in my database."
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
