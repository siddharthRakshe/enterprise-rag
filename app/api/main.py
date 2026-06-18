import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.rag_service import ask_question

app = FastAPI(title="Enterprise HR RAG API")

class QueryRequest(BaseModel):
    role: str
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/query", response_model=QueryResponse)
def handle_query(payload: QueryRequest):
    try:
        response_text = ask_question(role=payload.role, question=payload.question)
        return QueryResponse(answer=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Railway passes a dynamic port via environment variables
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)