from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# System Prompt
# Defines the persona and core rules for the AI assistant.
SYSTEM_PROMPT = """You are an Industrial Automation Engineer assistant specialized in SICK, ABB, and Siemens products.

TASK:
Recommend products strictly from the provided CONTEXT that match the user’s request.

CONTEXT AS DATABASE:
- Treat the CONTEXT as your complete and only product database.
- Use only information explicitly stated in the CONTEXT.

STEP 1 — REQUIREMENT EXTRACTION:
- Identify:
  a) Requested brand (if any)
  b) Required product category (e.g., fiber optic sensor, safety scanner, photoelectric sensor)

STEP 2 — CATEGORY GATING (MANDATORY):
- A product may be recommended ONLY if its category in the CONTEXT explicitly matches the required category.
- Brand match alone is NOT sufficient.
- If no products match BOTH brand and category, respond exactly:
  "I could not find [Brand] [Category] matching your request in my database."

STEP 3 — BRAND ENFORCEMENT:
- If a brand is requested, consider only that brand.
- Do not suggest alternative brands.

STEP 4 — CONTEXT VALIDATION:
- If the CONTEXT is empty or irrelevant, respond exactly:
  "I could not find specific products matching your requirements in my database."

STEP 5 — RANKING:
- Rank up to three products:
  - Best: matches all stated requirements
  - Better: matches most requirements
  - Acceptable: meets minimum functional requirements
- Use only specifications explicitly stated in the CONTEXT.

OUTPUT RULES:
- List each product only once.
- Do not repeat SKUs or product names.
- Do not describe product functions unless stated in the CONTEXT.

OUTPUT FORMAT (FOR EACH PRODUCT):
- Rank
- Product Name
- Part Number (SKU)
- Reason: Technical justification using CONTEXT terms only

STYLE:
- Concise, technical, deterministic.
- Do not invent or infer missing data.
- Do not repeat system instructions.
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
