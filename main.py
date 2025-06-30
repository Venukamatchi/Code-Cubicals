# ✅ main.py (Updated for Docker Public Deployment with Theme Toggle)

import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from datetime import datetime, timedelta
from collections import defaultdict
import json
import requests
import time

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Inventory Spotter AI",
    page_icon="📦",
    layout="wide"
)

# --- THEME TOGGLE ---
if 'dark_theme' not in st.session_state:
    st.session_state.dark_theme = False

# Theme toggle button in sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    theme_button = st.button("🌓 Toggle Theme", use_container_width=True)
    if theme_button:
        st.session_state.dark_theme = not st.session_state.dark_theme
        st.rerun()

# --- THEME STYLES ---
def get_theme_styles():
    if st.session_state.dark_theme:
        return """
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .stApp > div {
            color: #fafafa;
        }
        .big-title {
            font-size: 3rem;
            font-weight: bold;
            color: #fafafa;
            margin-bottom: 0.2em;
            letter-spacing: -1px;
        }
        .subtle {
            font-size: 1.1rem;
            color: #a0a0a0;
            margin-bottom: 1.2em;
        }
        .stTextInput>div>div>input {
            font-size: 20px;
            padding: 12px 18px;
            border-radius: 8px;
            border: 1.5px solid #3a3a3a;
            background-color: #1e1e1e;
            color: #fafafa !important;
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
        .stMarkdown h4 { color: #4f8cff; }
        .stMarkdown, .stMarkdown p, .stMarkdown div { 
            color: #fafafa !important; 
        }
        .stExpanderHeader { 
            font-size: 1.1rem; 
            color: #fafafa !important;
            background-color: #262730;
        }
        .stAlert { 
            background: #1a2332; 
            border-radius: 7px; 
            color: #fafafa !important;
        }
        hr { 
            border: 0; 
            border-top: 1.5px solid #3a3a3a; 
            margin: 2em 0; 
        }
        .example-card {
            background: #1a1a2e;
            border-radius: 8px;
            padding: 1em 1.5em;
            margin-bottom: 0.7em;
            border-left: 4px solid #4f8cff;
            font-size: 1.05em;
            color: #fafafa;
        }
        .stSuccess {
            background-color: #0f2027;
            color: #00ff88 !important;
        }
        .stError {
            background-color: #2a0a0a;
            color: #ff6b6b !important;
        }
        .stSpinner {
            color: #4f8cff;
        }
        .stSidebar {
            background-color: #0e1117;
        }
        .stSidebar .stMarkdown, .stSidebar .stMarkdown p, .stSidebar .stMarkdown div {
            color: #fafafa !important;
        }
        div[data-testid="stExpander"] {
            background-color: #1a1a2e;
            border: 1px solid #3a3a3a;
            color: #fafafa !important;
        }
        .stCodeBlock {
            background-color: #1e1e1e;
            color: #fafafa !important;
        }
        .stForm {
            background-color: #1a1a2e;
            border-radius: 8px;
            padding: 1em;
        }
        label[data-testid="stTextInputLabel"] {
            color: #fafafa !important;
        }
        </style>
        """
    else:
        return """
        <style>
        .stApp {
            background-color: #f6f8fa;
            color: #22223b;
        }
        .stApp > div {
            color: #22223b;
        }
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
            color: #22223b !important;
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
        .stMarkdown, .stMarkdown p, .stMarkdown div { 
            color: #22223b !important; 
        }
        .stExpanderHeader { 
            font-size: 1.1rem; 
            color: #3a3a3a !important;
        }
        .stAlert { 
            background: #e3f4fc; 
            border-radius: 7px; 
            color: #22223b !important;
        }
        hr { 
            border: 0; 
            border-top: 1.5px solid #e2e8f0; 
            margin: 2em 0; 
        }
        .example-card {
            background: #f1f5fb;
            border-radius: 8px;
            padding: 1em 1.5em;
            margin-bottom: 0.7em;
            border-left: 4px solid #4f8cff;
            font-size: 1.05em;
            color: #22223b;
        }
        .stSidebar {
            background-color: #ffffff;
        }
        .stSidebar .stMarkdown, .stSidebar .stMarkdown p, .stSidebar .stMarkdown div {
            color: #22223b !important;
        }
        div[data-testid="stExpander"] {
            color: #22223b !important;
        }
        .stForm {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 1em;
            border: 1px solid #e2e8f0;
        }
        label[data-testid="stTextInputLabel"] {
            color: #22223b !important;
        }
        </style>
        """

# Apply theme styles
st.markdown(get_theme_styles(), unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="big-title">📦 Inventory Spotter AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">🔍 Ask anything about warehouse stock, locations, or expiry paths.</div>', unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# --- EXAMPLES ---
with st.expander("💡 Example questions you can try", expanded=True):
    st.markdown("""
    <div class="example-card">What is the current stock of Digestive Biscuit?</div>
    <div class="example-card">Which items are located in Aisle F?</div>
    <div class="example-card">What's expiring in July?</div>
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
        llm=Ollama(model="phi3", base_url="http://host.containers.internal:11434"),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return qa_chain

# --- QUESTION FORM ---
st.markdown("<hr/>", unsafe_allow_html=True)
with st.form("query_form", clear_on_submit=False):
    query = st.text_input(
        "🔎 Ask your warehouse inventory question",
        placeholder="e.g. What items are in Aisle B or expiring in August?",
        key="user_query"
    )
    submitted = st.form_submit_button("Get Answer")

# --- ANSWER SECTION ---
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

# ================================
# 📞 PHONE CALL FEATURE SECTION
# ================================
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("### 📞 Trigger Inventory Voice Alert")

OMNI_API_KEY = "eCVeEkwvecsvqBCZJ_ZBQO_L65Es4u5WLduombR4qS8"
AGENT_ID = 2428
DATA_PATH = "data/processed/output.jsonl"

def load_inventory():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f]
    except Exception as e:
        st.error(f"Failed to load inventory: {e}")
        return []

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%m/%d/%Y")
        return True
    except:
        return False

def group_expiries_by_month(inventory):
    now = datetime.now()
    next_month = now + timedelta(days=32)
    expiry_map = defaultdict(list)
    for item in inventory:
        date_str = item.get("Expiration_Date", "")
        if not is_valid_date(date_str):
            continue
        date = datetime.strptime(date_str, "%m/%d/%Y")
        if now <= date <= next_month:
            key = date.strftime("%B %Y")
            expiry_map[key].append(item)
    return expiry_map

def generate_alert_text(monthly_expiries):
    if not monthly_expiries:
        return "Hello. No items are expiring in the next month. Thank you."
    parts = ["Hello. This is your Inventory Assistant. Here is your expiry report."]
    for month, items in monthly_expiries.items():
        parts.append(f"\nIn {month}, these items are expiring:")
        for itm in items[:10]:
            parts.append(
                f"- {itm['Name']} (ID: {itm['Item_ID']}), Aisle {itm.get('Aisle','?')} Shelf {itm.get('Shelf','?')}, Qty: {itm.get('Stock_Quantity','?')}"
            )
        if len(items) > 10:
            parts.append(f"...and {len(items) - 10} more items.")
    parts.append("Please review your inventory dashboard. Goodbye.")
    return " ".join(parts)

def send_voice_alert(agent_id, phone_number, message):
    url = "https://backend.omnidim.io/api/v1/calls/dispatch"
    headers = {
        "Authorization": f"Bearer {OMNI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "agent_id": agent_id,
        "to_number": phone_number,
        "call_context": {
            "message": message
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code, response.text

with st.form("call_form"):
    phone = st.text_input("📱 Enter phone number with country code", value="+91", key="phone_input")
    call_submit = st.form_submit_button("🚀 Call Now")

if call_submit:
    with st.spinner("⏳ Preparing and sending your voice alert..."):
        inventory = load_inventory()
        if inventory:
            expiries = group_expiries_by_month(inventory)
            message = generate_alert_text(expiries)
            status, response = send_voice_alert(AGENT_ID, phone, message)
            if status == 200:
                st.success(f"✅ Voice call sent to {phone}")
            else:
                st.error(f"❌ Failed to send call: {response}")
        else:
            st.error("❌ No inventory data found.")

# --- SIDEBAR INFO ---
with st.sidebar:
    st.markdown("---")
    current_theme = "🌙 Dark Mode" if st.session_state.dark_theme else "☀️ Light Mode"
    st.markdown(f"**Current Theme:** {current_theme}")
    
    st.markdown("### 📊 App Features")
    st.markdown("""
    - **Smart Inventory Search** 🔍
    - **Voice Alerts** 📞
    - **Expiry Tracking** ⏰
    - **Location Mapping** 📍
    - **Dark/Light Themes** 🌓
    """)

# --- FOOTER ---
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:#6c757d; font-size: 0.97em;">
🧠 Powered by <b>LangChain</b>, <b>Ollama (phi3)</b>, <b>FAISS</b> & <b>OmniDimension Voice</b> | Made for smarter warehouses 📞
</div>
""", unsafe_allow_html=True)
