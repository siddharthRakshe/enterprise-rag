from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


# Step 1: Load PDF
loader = PyPDFLoader("documents/HR_Policy.pdf")
documents = loader.load()


# Step 2: Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)

chunks = splitter.split_documents(documents)


# Step 3: Load embedding model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Step 4: Convert chunks into embeddings
texts = [
    chunk.page_content
    for chunk in chunks
]

embeddings = model.encode(texts)


# Step 5: Display results
print("\n===== EMBEDDINGS =====\n")

for i, embedding in enumerate(embeddings, start=1):
    print(f"Chunk {i}")
    print("Text:")
    print(texts[i-1])

    print("\nVector dimensions:")
    print(len(embedding))

    print("\nFirst 10 numbers:")
    print(embedding[:10])

    print("\n" + "-" * 50)