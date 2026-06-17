from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.models import ChatRequest, ChatResponse
from app.services.rag_service import ask_question

from app.database.connection import get_db

from app.auth.schemas import UserRegister, UserResponse
from app.auth.login_schema import UserLogin

from app.auth.crud import (
    create_user,
    authenticate_user
)

from app.security.jwt_handler import create_access_token
from app.security.dependencies import get_current_user


app = FastAPI(
    title="Enterprise Secure RAG API"
)


# ==============================
# Health Check
# ==============================

@app.get("/")
def home():
    return {
        "message": "Enterprise Secure RAG API is running!"
    }


# ==============================
# Secure RAG Chat Endpoint
# JWT extracts the role automatically
# ==============================

@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):

    answer = ask_question(
        role=current_user["role"],
        question=request.question
    )

    return ChatResponse(
        answer=answer
    )


# ==============================
# User Registration
# ==============================

@app.post(
    "/register",
    response_model=UserResponse
)
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    try:
        new_user = create_user(
            db,
            user
        )

        return new_user

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ==============================
# User Login + JWT Generation
# ==============================

@app.post("/login")
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db,
        user_data.email,
        user_data.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    access_token = create_access_token(
        {
            "user_id": user.id,
            "username": user.username,
            "role": user.role
        }
    )


    return {
        "access_token": access_token,
        "token_type": "bearer"
    }