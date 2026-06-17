from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    Request model for protected RAG chat.
    JWT will provide the user role.
    """
    question: str


class ChatResponse(BaseModel):
    """
    Response model for RAG answer.
    """
    answer: str