import streamlit as st
import requests
import pandas as pd
import json
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000/api/v1")

st.set_page_config(page_title="Industrial AI Engine", layout="wide")
st.title("🏭 Industrial Automation AI Engine")

# Sidebar
st.sidebar.header("Configuration")
api_status = "🔴 Offline"
try:
    health = requests.get(f"{API_BASE_URL}/health", timeout=2)
    if health.status_code == 200:
        api_status = "🟢 Online"
except:
    pass
st.sidebar.markdown(f"API Status: {api_status}")

# Tabs
tab1, tab2 = st.tabs(["💬 AI Assistant", "📄 Quotation Generator"])

# --- TAB 1: RAG CHAT ---
with tab1:
    st.header("Technical Sales Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about SICK, ABB, or Siemens products..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/recommend",
                        json={"query": prompt},
                        timeout=120
                    )
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "No answer provided.")
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # Show sources if available
                        if "sources" in data:
                            with st.expander("View Source Documents"):
                                for idx, source in enumerate(data["sources"]):
                                    st.markdown(f"### {idx+1}. {source.get('name')} ({source.get('sku')})")
                                    st.caption(f"Category: {source.get('category')} | Match Score: {source.get('score', 0):.2f}")
                                    
                                    # 1. Technical Drawings / Images
                                    drawings = source.get('technical_drawings', [])
                                    if drawings:
                                        st.markdown("**Technical Drawings:**")
                                        # Display first drawing for now
                                        st.image(drawings[0], caption="Technical Drawing", width=400)
                                    
                                    # 2. Documents
                                    docs = source.get('documents', [])
                                    if docs:
                                        st.markdown("**Documents:**")
                                        for d in docs:
                                            st.markdown(f"- 📄 [{d.get('title', 'Document')}]({d.get('url')})")
                                    
                                    # 3. Specifications
                                    specs = source.get('specifications', {})
                                    if specs:
                                        with st.expander("Technical Specifications"):
                                            st.json(specs)
                                    
                                    st.divider()
                                # Fallback raw view
                                # st.json(data["sources"])
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# --- TAB 2: QUOTATION ---
with tab2:
    st.header("Generate Quotation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        customer_name = st.text_input("Customer Name", "Acme Corp")
        customer_email = st.text_input("Customer Email", "procurement@acme.com")
    
    st.subheader("Line Items")
    
    # Session state for items
    if "quote_items" not in st.session_state:
        st.session_state.quote_items = [{"sku": "", "name": "", "qty": 1, "price": 0.0}]

    def add_item():
        st.session_state.quote_items.append({"sku": "", "name": "", "qty": 1, "price": 0.0})

    for i, item in enumerate(st.session_state.quote_items):
        c1, c2, c3, c4 = st.columns([2, 3, 1, 2])
        item["sku"] = c1.text_input(f"SKU ##{i+1}", item["sku"], key=f"sku_{i}")
        item["name"] = c2.text_input(f"Product Name ##{i+1}", item["name"], key=f"name_{i}")
        item["qty"] = c3.number_input(f"Qty ##{i+1}", min_value=1, value=item["qty"], key=f"qty_{i}")
        item["price"] = c4.number_input(f"Price ($) ##{i+1}", min_value=0.0, value=item["price"], step=10.0, key=f"price_{i}")

    st.button("Add Item", on_click=add_item)
    
    if st.button("Generate PDF Quote", type="primary"):
        payload = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "items": st.session_state.quote_items
        }
        
        with st.spinner("Generating PDF..."):
            try:
                # Use stream=True to handle binary file
                res = requests.post(f"{API_BASE_URL}/quotations", json=payload, stream=True)
                
                if res.status_code == 200:
                    st.success("Quotation generated successfully!")
                    st.download_button(
                        label="Download PDF",
                        data=res.content,
                        file_name="quotation.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error(f"Failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
