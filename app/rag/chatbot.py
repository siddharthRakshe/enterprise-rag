import os

from app.guardrails.context_guard import check_context_relevance
from app.guardrails.prompt_guard import check_prompt_safety
from app.guardrails.pii_guard import check_pii_request
from app.guardrails.output_guard import check_output_safety

from app.security.rbac import check_permission
from app.security.permission_mapper import get_required_permission

from app.logging.audit_logger import log_event

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_groq import ChatGroq


# ==================================================
# Load Embedding Model
# ==================================================

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ==================================================
# Connect ChromaDB
# ==================================================

vector_db = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)


# ==================================================
# Load Groq LLM
# ==================================================

llm = ChatGroq(
    model_name="llama3-8b-8192",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)


# ==================================================
# Start Application
# ==================================================

print("\n🛡️ Enterprise RAG Assistant Started")

print("\nAvailable Roles:")
print("employee")
print("manager")
print("hr_admin")
print("finance")
print("admin")

user_role = input("\nEnter your role: ").strip().lower()

print("\nLogged in as:", user_role)
print("Type 'exit' to quit.\n")


# ==================================================
# Chat Loop
# ==================================================

while True:

    question = input("You: ").strip()

    if question.lower() == "exit":
        print("\n👋 Goodbye!")
        break

    # ==================================================
    # RBAC Permission Check
    # ==================================================

    required_permission = get_required_permission(question)

    if not check_permission(user_role, required_permission):

        log_event(
            user_role,
            question,
            "ACCESS_DENIED",
            "RBAC permission failed"
        )

        print(
            "\n🔐 Assistant: You are not authorized to access this information."
        )

        print("\n" + "=" * 60)
        continue

    # ==================================================
    # Prompt Guard
    # ==================================================

    if not check_prompt_safety(question):

        log_event(
            user_role,
            question,
            "PROMPT_ATTACK",
            "Prompt injection detected"
        )

        print(
            "\n🚫 Assistant: Unsafe prompt detected. Request rejected."
        )

        print("\n" + "=" * 60)
        continue

    # ==================================================
    # PII Guard
    # ==================================================

    if not check_pii_request(question):

        log_event(
            user_role,
            question,
            "PII_BLOCKED",
            "Sensitive information request blocked"
        )

        print(
            "\n🔒 Assistant: Access to sensitive personal information is restricted."
        )

        print("\n" + "=" * 60)
        continue

    # ==================================================
    # Retrieve Context
    # ==================================================

    results = vector_db.similarity_search_with_score(
        question,
        k=2
    )

    if not check_context_relevance(results):

        log_event(
            user_role,
            question,
            "NO_CONTEXT",
            "No relevant document found"
        )

        print(
            "\n🤖 Assistant: I don't have enough information in the HR policy."
        )

        print("\n" + "=" * 60)
        continue

    docs = [doc for doc, score in results]

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    # ==================================================
    # Prompt
    # ==================================================

    prompt = f"""
You are an Enterprise HR Assistant.

Rules:
1. Answer only from the HR policy context.
2. Do not invent information.
3. If information is unavailable, say you don't know.
4. Keep answers professional.

HR Context:
{context}

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    # ==================================================
    # Output Guard
    # ==================================================

    if not check_output_safety(response.content):

        log_event(
            user_role,
            question,
            "OUTPUT_BLOCKED",
            "Unsafe response blocked"
        )

        print(
            "\n🛑 Assistant: Response blocked due to security policy."
        )

        print("\n" + "=" * 60)
        continue

    # ==================================================
    # Success Log
    # ==================================================

    log_event(
        user_role,
        question,
        "QUERY_SUCCESS",
        "Response generated successfully"
    )

    print("\n🤖 Assistant:")
    print(response.content)

    print("\n" + "=" * 60)