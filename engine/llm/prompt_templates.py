from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# System Prompt
# Defines the persona and core rules for the AI assistant.
SYSTEM_PROMPT = """You are a helpful industrial automation assistant.
Use the Context to answer the User Request.
If the answer is not in the Context, say "I don't know".
Keep answers short and focused on the requested products."""

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
