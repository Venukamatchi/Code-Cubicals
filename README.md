# 📦 Inventory Spotter AI

**Inventory Spotter AI** is an end-to-end, AI-powered warehouse inventory assistant. It processes a grocery warehouse dataset, detects items expiring soon, generates embeddings for semantic search, enables intelligent Q&A via a chatbot, dispatches expiry alerts via voice call, and provides a beautiful Streamlit dashboard for interactive queries. 

---

## 🚀 Features

- **Data Pipeline**: Cleans and processes inventory CSVs, flags items expiring soon, and outputs a structured JSONL file.
- **Embeddings & Semantic Search**: Converts inventory records into vector embeddings using HuggingFace and FAISS for fast, context-aware retrieval.
- **Conversational QA**: Uses LangChain + Ollama (phi3) to answer natural language queries about your stock, locations, or expiry details.
- **Voice Alerts**: Aggregates expiry information and sends automated voice calls via OmniDimension for proactive inventory management.
- **Streamlit Dashboard**: Sleek web UI with example queries, styled components, and instant answers with source traceability.
- **Pathway Integration**: Utilizes [Pathway](https://pathway.com) for high-performance, scalable, and reactive data pipelines to process large inventory datasets efficiently.

---

## 🏗️ Full System Structure & Workflow

### 1. **Data Input & Validation (Pathway)**
- **File Structure:**
  - `data/uploads/Grocery_Inventory_and_Sales_Dataset.csv` – Main input CSV.
- **Validation:**
  - Checks if the file exists. If missing, logs an error and stops execution.
  - Defines a strict schema via `InputSchema` using Pathway.
  - Validates column existence and types (e.g., `Stock_Quantity` must be int).
  - Invalid/malformed dates or missing fields are logged and not processed for expiry logic.
- **Processing Steps:**
  - Reads CSV via Pathway’s streaming API.
  - Selects important columns and renames them for downstream use.
  - Adds a computed `Expiring_Soon` flag (checks if items will expire within 7 days).
  - Writes the cleaned and validated data to `data/processed/output.jsonl`.

### 2. **Embeddings Generation & Indexing**
- **File Structure:**
  - `embed_inventory.py`
  - `vectorstore/faiss_index/` – FAISS vector index for semantic search.
- **Steps:**
  - Loads `output.jsonl` and summarizes each record as a document.
  - Embeds these using HuggingFace (`all-MiniLM-L6-v2`).
  - Stores vectors in FAISS for fast context-aware retrieval.

### 3. **Conversational Q&A with LangChain and Ollama**
- **Files:**
  - Console QA: Inline in your scripts (`main_pipeline.py` or similar).
  - Streamlit UI: `app.py`
- **Steps:**
  - Loads the FAISS vectorstore.
  - For each user query, retrieves the top-k relevant inventory records.
  - Uses LangChain’s RetrievalQA pipeline with Ollama (phi3 model) to generate answers, using the retrieved context.
  - Displays both the answer and the supporting source snippets.

### 4. **Voice Alerts via OmniDimension**
- **File:** `voice_alerts.py`
- **How It Works:**
  - Loads `output.jsonl`.
  - Groups inventory items expiring in the next two months, by month.
  - Generates a summary message (lists items, locations, stock, etc).
  - Uses the [OmniDimension API](https://omnidimension.com) to send a phone call:
    - Requires your OmniDimension API key, agent ID, and target phone number.
    - If no items are expiring soon, delivers a “no expiry” message.
  - **Input Validations:**
    - Ensures required credentials are set.
    - Only includes valid dates in expiry calculations.
    - Skips and logs records with missing/invalid date fields.

### 5. **Interactive Dashboard (Streamlit)**
- **File:** `app.py`
- **Features:**
  - Modern UI with branding, styled components, and example queries.
  - Accepts free-text questions and displays answers and sources.
  - Uses the same QA retrieval chain as the CLI, but in a web interface.

---

## 🗂️ Top-to-Bottom Project Structure

```
.
├── data/
│   ├── uploads/
│   │   └── Grocery_Inventory_and_Sales_Dataset.csv      # INPUT: Raw inventory CSV
│   └── processed/
│       └── output.jsonl                                 # OUTPUT: Cleaned, flagged inventory data
├── vectorstore/
│   └── faiss_index/                                     # FAISS vector index for embeddings
├── main_pipeline.py                                     # ALL: Pathway pipeline (ETL, validation, flagging)
├── embed_inventory.py                                   # Embedding inventory docs & building FAISS index
├── voice_alerts.py                                      # Generates & sends expiry voice alerts via OmniDimension
├── app.py                                               # Streamlit dashboard for Q&A
└── README.md                                            # This file
```

---

## 💡 Example Workflow

1. **Ingest & Clean Data**  
   - User puts a CSV in `data/uploads/`.
   - Pathway pipeline validates & processes, outputting a JSONL.

2. **Embed & Index**  
   - `embed_inventory.py` reads JSONL, creates document embeddings, and builds a FAISS index.

3. **Ask Questions (CLI or UI)**  
   - User asks inventory questions via terminal or Streamlit app.
   - System retrieves relevant docs using FAISS + HuggingFace + LangChain.
   - Answers are generated using Ollama LLM, with source snippets cited.

4. **Voice Alerts**  
   - `voice_alerts.py` runs (manually or on schedule).
   - Finds items expiring in next 2 months, generates a message, and calls the manager via OmniDimension.

---

## 🔎 Details: Pathway & OmniDimension Usage

- **Pathway**  
  - Powers the full ETL pipeline: input file validation, schema enforcement, row-wise cleaning, date parsing, and flagging for imminent expiry.
  - Ensures only valid, consistent, and useful data is passed to downstream tasks.
  - Graceful handling of invalid rows (logs and skips).

- **OmniDimension**  
  - Handles automated voice alerts.
  - Accepts a summary message and calls the provided phone number.
  - Ensures decision makers are aware of upcoming expiry risks, directly via phone.

---

## 🧠 How Input is Validated

- **File Presence**: Fails early if the input CSV is missing.
- **Schema Check**: Uses Pathway schema, raises errors for missing/invalid columns.
- **Type Checks**: Coerces and checks types (e.g., `int`, `str`, date parsing).
- **Date Handling**: Invalid or missing dates are logged and not included in expiry calculations.
- **Logging**: All validation errors are logged, including row counts and any fallback logic.

---

## 💡 Example Queries

- *What is the current stock of Digestive Biscuit?*
- *Which items are located in Aisle F?*
- *What’s expiring in July?*
- *Where is Basmati Rice stored?*

---

## 🔐 Security & Privacy

- All data is processed and stored locally.
- Voice call features require your OmniDimension credentials; **never share your secrets** publicly.
- Ollama LLM runs locally, so your queries never leave your machine.

---

## 🤝 Credits

- [Pathway](https://pathway.com) for efficient streaming data processing
- [LangChain](https://langchain.com) for LLM orchestration
- [Ollama](https://ollama.com) for local, privacy-preserving LLM inference
- [FAISS](https://github.com/facebookresearch/faiss) for fast vector search
- [OmniDimension](https://omnidimension.com) for AI-powered voice calling

---

## 🛠️ Troubleshooting

- **Ollama not running?**  
  Run `ollama serve` and pull the `phi3` model:  
  `ollama pull phi3`
- **CSV file not found?**  
  Ensure your CSV is at `data/uploads/Grocery_Inventory_and_Sales_Dataset.csv`.
- **Voice call failed?**  
  Check your API key, agent ID, and phone number. See logs for details.

---

## 📜 License

MIT License. See `LICENSE` file for details.

---

## ✨ Demo Screenshots

*(Add your screenshots or GIFs here!)*

---

**Inventory Spotter AI — The smarter way to manage your warehouse.** 🚛
