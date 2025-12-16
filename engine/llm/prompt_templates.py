from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# System Prompt
# Defines the persona and core rules for the AI assistant.
SYSTEM_PROMPT = """You are an Industrial Automation Engineer assistant.

Your job is to recommend SICK, ABB, or Siemens products ONLY from the provided CONTEXT.

IMPORTANT:
- The CONTEXT is your entire database.
- If information is not in the CONTEXT, it does not exist.
- Do NOT output instructions, rules, headings, or explanations about your process.

STEP 1: UNDERSTAND THE REQUEST
- Identify the requested brand (if any).
- Identify the required product category (for example: fiber optic sensor).

STEP 2: FILTER PRODUCTS
- Consider ONLY products from the requested brand.
- Consider ONLY products whose category in the CONTEXT EXACTLY matches the requested category.

STEP 3: FAILURE CONDITIONS
- If no products match both brand and category, respond EXACTLY with:
  "I could not find SICK fiber optic sensors matching your request in my database."

STEP 4: OUTPUT (ONLY IF MATCHES EXIST)
- List up to THREE products.
- Each product may appear ONLY ONCE.
- Rank them as: Best, Better, or Acceptable.

FOR EACH PRODUCT OUTPUT EXACTLY:
Rank:
Product Name:
Part Number (SKU):
Reason: (use only information explicitly stated in the CONTEXT)

STYLE:
- Technical, concise.
- No guessing.
- No repetition.
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
