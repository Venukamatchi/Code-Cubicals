import json
import os

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# Constants for file paths
DATA_PATH = "data/processed/output.jsonl"
VECTOR_INDEX_PATH = "vectorstore/faiss_index"

def load_inventory_documents(path: str) -> list[Document]:
    """
    Load inventory data from JSONL and convert each record into a LangChain Document.
    Each document's content summarizes the product info and metadata preserves the full record.
    """
    documents = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line.strip())
            content = (
                f"Product: {rec.get('Name', 'N/A')}\n"
                f"Location: {rec.get('Warehouse_Location', 'N/A')}\n"
                f"Expiration: {rec.get('Expiration_Date', 'N/A')}\n"
                f"Expiring Soon: {rec.get('Expiring_Soon', False)}\n"
                f"Stock Quantity: {rec.get('Stock_Quantity', 'N/A')}\n"
                f"Aisle: {rec.get('Aisle', 'N/A')}\n"
                f"Shelf: {rec.get('Shelf', 'N/A')}"
            )
            documents.append(Document(page_content=content, metadata=rec))
    return documents

def embed_documents(documents: list[Document]) -> FAISS:
    """
    Create embeddings for documents using HuggingFace embeddings and return a FAISS vectorstore.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore

def save_vectorstore(vectorstore: FAISS, path: str):
    """
    Save the FAISS vectorstore to a local directory.
    """
    os.makedirs(path, exist_ok=True)
    vectorstore.save_local(path)

if __name__ == "__main__":
    print("🔄 Loading inventory documents...")
    docs = load_inventory_documents(DATA_PATH)
    print(f"🧠 Creating embeddings for {len(docs)} documents...")
    vectorstore = embed_documents(docs)
    print(f"💾 Saving vectorstore to {VECTOR_INDEX_PATH} ...")
    save_vectorstore(vectorstore, VECTOR_INDEX_PATH)
    print("✅ Vectorstore saved successfully!")

