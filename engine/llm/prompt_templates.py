from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# System Prompt
# Defines the persona and core rules for the AI assistant.
SYSTEM_PROMPT = """You are an Industrial Automation Engineer.
Your goal is to recommend SICK, ABB, or Siemens products from the CONTEXT.

### RESPONSE RULES:
1. **Direct Answer Only**: Do NOT repeat the question, do NOT mention your instructions, and do NOT say "Based on the context". Start directly with the recommendation.
2. **Strict Filtering**: Only recommend products from the requested Brand and Category found in the CONTEXT.
3. **No Matches**: If nothing matches, say exactly: "I could not find [Brand] [Category] in the database."

### OUTPUT FORMAT:
For each matching product (Max 3), use this EXACT Markdown structure:

**Rank:** [Best / Better / Acceptable]
**Product:** [Product Name]
**SKU:** [Part Number]
**Reason:** [Technical explanation from CONTEXT]

---

### STYLE:
- Professional, technical, concise.
- Use bolding for key terms.
- No conversational filler.
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
