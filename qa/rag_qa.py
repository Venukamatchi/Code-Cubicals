from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import warnings

# Suppress known LangChain warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

# Load the FAISS vectorstore with HuggingFace embeddings
print("📦 Loading vectorstore...")
vectorstore = FAISS.load_local(
    "vectorstore/faiss_index",
    embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
    allow_dangerous_deserialization=True
)

# Create retriever with top 5 results per query
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Define the prompt template for the QA chain
template = """
You are an inventory assistant AI. Use the context to answer the user query.
If the answer is not in the context, say you don't know.

Context:
{context}

Question: {question}
Answer:
"""

prompt = PromptTemplate(input_variables=["context", "question"], template=template)

# Initialize the RetrievalQA chain with Ollama LLM
qa_chain = RetrievalQA.from_chain_type(
    llm=Ollama(model="phi3"),  # Change model here if needed
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

# Interactive Q&A loop
if __name__ == "__main__":
    print("🤖 InventoryBot ready. Type your question or 'exit' to quit.")
    while True:
        query = input("\n🔎 Ask InventoryBot: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("👋 Exiting InventoryBot. Have a great day!")
            break

        try:
            result = qa_chain(query)
            print("\n📤 Answer:", result["result"])

            print("\n📚 Source Snippets:")
            for doc in result["source_documents"]:
                print("-", doc.page_content)
        except Exception as e:
            print(f"❌ Error processing query: {e}")

