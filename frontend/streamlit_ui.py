import streamlit as st
from qa.rag_qa import ask

st.set_page_config(page_title="Inventory Spotter AI", page_icon="📦")
st.title("📦 Inventory Spotter AI")
st.caption("Real-time warehouse copilot")

query = st.text_input("🔎 Ask about inventory (e.g., 'What items are about to expire?')")
if query:
    response = ask(query)
    st.success(response)

