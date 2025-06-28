import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import time

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Inventory Spotter AI",
    page_icon="📦",
    layout="wide"
)

# --- CUSTOM STYLES ---
st.markdown("""
<style>
body { background-color: #f6f8fa; }
.big-title {
    font-size: 3rem;
    font-weight: bold;
    color: #22223b;
    margin-bottom: 0.2em;
    letter-spacing: -1px;
}
.subtle {
    font-size: 1.1rem;
    color: #6c757d;
    margin-bottom: 1.2em;
}
.stTextInput>div>div>input {
    font-size: 20px;
    padding: 12px 18px;
    border-radius: 8px;
    border: 1.5px solid #d1d5db;
    background-color: #f8fafc;
}
.stButton>button {
    background: linear-gradient(90deg,#4f8cff 0,#38b6ff 100%);
    color: white;
    font-weight: 600;
    border-radius: 7px;
    padding: 0.6em 2em;
    margin-top: 1em;
    transition: background 0.2s;
}
.stButton>button:hover {
    background: linear-gradient(90deg,#38b6ff 0,#4f8cff 100%);
}
.stMarkdown h4 { color: #1f77b4; }
.stExpanderHeader { font-size: 1.1rem; color: #3a3a3a; }
.stAlert { background: #e3f4fc; border-radius: 7px; }
hr { border: 0; border-top: 1.5px solid #e2e8f0; margin: 2em 0; }
# Custom cards for examples
.example-card {
    background: #f1f5fb;
    border-radius: 8px;
    padding: 1em 1.5em;
    margin-bottom: 0.7em;
    border-left: 4px solid #4f8cff;
    font-size: 1.05em;
}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="big-title">📦 Inventory Spotter AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">🔍 Ask anything about warehouse stock, locations, or expiry paths.</div>', unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# --- EXAMPLES ---
with st.expander("💡 Example questions you can try", expanded=True):
    st.markdown("""
    <div class="example-card">What is the current stock of Digestive Biscuit?</div>
    <div class="example-card">Which items are located in Aisle F?</div>
    <div class="example-card">What’s expiring in July?</div>
    <div class="example-card">Where is Basmati Rice stored?</div>
    """, unsafe_allow_html=True)

# --- LOAD CHAIN ---
@st.cache_resource
def load_chain():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.load_local("vectorstore/faiss_index", embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are an inventory assistant AI. Use the context to answer the user query. If the answer is not in the context, say you don't know.

Context: {context}
Question: {question}
Answer:"""
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=Ollama(model="phi3"),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain

# --- INPUT ---
st.markdown("<hr/>", unsafe_allow_html=True)
with st.form("query_form", clear_on_submit=False):
    query = st.text_input(
        "🔎 Ask your warehouse inventory question",
        placeholder="e.g. What items are in Aisle B or expiring in August?",
        key="user_query"
    )
    submitted = st.form_submit_button("Get Answer")

# --- ANSWER ---
if submitted and query:
    with st.spinner("🤖 Thinking..."):
        qa_chain = load_chain()
        time.sleep(0.5)
        result = qa_chain.invoke(query)
    st.markdown("### ✅ Answer:")
    st.success(result['result'])
    st.markdown("### 📚 Source Documents")
    for i, doc in enumerate(result["source_documents"], start=1):
        with st.expander(f"📄 Snippet {i}"):
            st.code(doc.page_content, language="text")

# --- FOOTER ---
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#6c757d; font-size: 0.97em;">
🧠 Powered by <b>LangChain</b>, <b>Ollama (phi3)</b> and <b>FAISS</b> &nbsp;|&nbsp; Created for real-time warehouse insights 🚛
</div>
""", unsafe_allow_html=True)

