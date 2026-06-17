from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Step 1: Load the PDF
loader = PyPDFLoader("documents/HR_Policy.pdf")
documents = loader.load()


# Step 2: Create a text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)


# Step 3: Split the document into chunks
chunks = text_splitter.split_documents(documents)


# Step 4: Print the chunks
print("\n===== DOCUMENT CHUNKS =====\n")

for i, chunk in enumerate(chunks, start=1):
    print(f"\n----- Chunk {i} -----")
    print(chunk.page_content)

