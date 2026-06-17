from langchain_community.document_loaders import PyPDFLoader

# Path to your PDF file
pdf_path = "documents/HR_Policy.pdf"

# Create PDF loader
loader = PyPDFLoader(pdf_path)

# Load PDF pages
documents = loader.load()

# Print extracted content
print("\n===== PDF CONTENT =====\n")

for page_number, document in enumerate(documents, start=1):
    print(f"\n--- Page {page_number} ---")
    print(document.page_content)