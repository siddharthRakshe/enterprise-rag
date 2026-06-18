from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq

from app.config import GROQ_API_KEY, MODEL_NAME
from app.guardrails.context_guard import check_context_relevance
from app.guardrails.prompt_guard import check_prompt_safety
from app.guardrails.pii_guard import check_pii_request
from app.guardrails.output_guard import check_output_safety

from app.security.rbac import check_permission
from app.security.permission_mapper import get_required_permission
from app.logging.audit_logger import log_event

# ==========================================
# Load Embedding Model
# ==========================================
print("🔄 Loading Embedding Model...")
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
print("✅ Embedding Model Loaded")

# ==========================================
# Load PDF
# ==========================================
print("🔄 Loading HR Policy PDF...")
loader = PyPDFLoader("documents/HR_Policy.pdf")
documents = loader.load()
print("✅ PDF Loaded Successfully")
print(f"📄 Pages Found: {len(documents)}")

# ==========================================
# Split Documents
# ==========================================
# NOTE: 100 characters is quite small for complex HR policies. 
# Consider increasing this (e.g., chunk_size=500, overlap=50) if answers lack context.
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, 
    chunk_overlap=20
)
chunks = splitter.split_documents(documents)
print(f"✅ Chunks Created: {len(chunks)}")

# ==========================================
# Create Chroma Vector Database
# ==========================================
# ==========================================
# Create / Load Chroma Vector Database
# ==========================================
print("🔄 Initializing Vector Database...")

# Using a persistent directory so data survives Railway deployment restarts
PERSIST_DIRECTORY = "chroma_db"

vector_db = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embedding_model
)

try:
    count = vector_db._collection.count()
    if count == 0:
        print("📥 Vector store empty. Loading and indexing HR Policy PDF...")
        loader = PyPDFLoader("documents/HR_Policy.pdf")
        documents = loader.load()
        
        # Increased chunk size to 500 characters so sentences don't get cut in half
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)
        
        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=PERSIST_DIRECTORY
        )
        print(f"✅ Indexed and stored {vector_db._collection.count()} chunks.")
    else:
        print(f"📚 Loaded existing vector store with {count} documents.")
except Exception as e:
    print(f"⚠️ Vector DB initialization: {e}")
# ==========================================
# Load Groq LLM
# ==========================================
print("🔄 Loading Groq Model...")
llm = ChatGroq(
    model_name=MODEL_NAME,
    groq_api_key=GROQ_API_KEY,
    temperature=0
)
print("✅ Groq Model Loaded")
print(f"🤖 Model Name: {MODEL_NAME}")
print("✅ RAG Service Loaded Successfully")


# ==========================================
# Main Enterprise RAG Function
# ==========================================
def ask_question(role: str, question: str):
    # --------------------------------------
    # RBAC Authorization
    # --------------------------------------
    required_permission = get_required_permission(question)

    if not check_permission(role, required_permission):
        log_event(
            role,
            question,
            "ACCESS_DENIED",
            "RBAC permission failed"
        )
        return "You are not authorized to access this information."

    # --------------------------------------
    # Prompt Injection Guard
    # --------------------------------------
    if not check_prompt_safety(question):
        log_event(
            role,
            question,
            "PROMPT_ATTACK",
            "Prompt injection detected"
        )
        return "Unsafe prompt detected. Request rejected."

    # --------------------------------------
    # PII Protection
    # --------------------------------------
    if not check_pii_request(question):
        log_event(
            role,
            question,
            "PII_BLOCKED",
            "Sensitive information requested"
        )
        return "Access to sensitive personal information is restricted."

    # --------------------------------------
    # Retrieve Documents
    # --------------------------------------
    results = vector_db.similarity_search_with_score(
        question,
        k=2
    )

    # --------------------------------------
    # Context Relevance Check
    # --------------------------------------
    if not check_context_relevance(results):
        log_event(
            role,
            question,
            "NO_CONTEXT",
            "No relevant information found"
        )
        return (
            "I don't have enough information "
            "in the HR policy to answer that question."
        )

    # --------------------------------------
    # Prepare Context
    # --------------------------------------
    docs = [doc for doc, score in results]
    context = "\n\n".join(doc.page_content for doc in docs)

    # --------------------------------------
    # Create Prompt (Fixed stray markdown syntax)
    # --------------------------------------
    prompt = f"""
You are an Enterprise HR Assistant.

Rules:
1. Answer only from the HR policy context.
2. Never make up information.
3. If information is unavailable, say: "I don't have enough information in the HR policy."
4. Keep answers professional.

HR Policy Context:
{context}

User Question:
{question}

Answer:
"""

    # --------------------------------------
    # Generate Response
    # --------------------------------------
    response = llm.invoke(prompt)
    answer = response.content

    # --------------------------------------
    # Output Guard
    # --------------------------------------
    if not check_output_safety(answer):
        log_event(
            role,
            question,
            "OUTPUT_BLOCKED",
            "Unsafe LLM response blocked"
        )
        return "Response blocked due to security policy."

    # --------------------------------------
    # Audit Success
    # --------------------------------------
    log_event(
        role,
        question,
        "QUERY_SUCCESS",
        "Response generated successfully"
    )

    return answer