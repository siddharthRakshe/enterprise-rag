from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


# Step 1: Load the same embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Step 2: Load existing ChromaDB
vector_db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)


# Step 3: Create a retriever
retriever = vector_db.as_retriever(
    search_kwargs={"k": 2}
)


# Step 4: Ask a question
query = "How many leaves do employees get?"


# Step 5: Search relevant chunks
results = retriever.invoke(query)


# Step 6: Display results
print("\n===== RETRIEVED RESULTS =====\n")

for i, doc in enumerate(results, start=1):
    print(f"Result {i}")
    print(doc.page_content)
    print("-" * 50)