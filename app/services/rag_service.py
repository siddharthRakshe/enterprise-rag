from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

from app.config import (
    OLLAMA_BASE_URL,
    MODEL_NAME
)

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

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ==========================================
# Load Chroma Vector Database
# ==========================================

vector_db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)


# ==========================================
# Load Ollama LLM from .env
# ==========================================

llm = ChatOllama(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    temperature=0
)


print("✅ RAG Service Loaded Successfully")


# ==========================================
# Main Enterprise RAG Function
# ==========================================

def ask_question(role, question):

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

    docs = [
        doc for doc, score in results
    ]

    context = "\n\n".join(
        doc.page_content for doc in docs
    )


    # --------------------------------------
    # Create LLM Prompt
    # --------------------------------------

    prompt = f"""
You are an Enterprise HR Assistant.

Rules:
1. Answer only from the HR policy context.
2. Never make up information.
3. If the answer is unavailable say:
"I don't have enough information in the HR policy."

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


    # --------------------------------------
    # Output Guard
    # --------------------------------------

    if not check_output_safety(response.content):

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


    return response.content