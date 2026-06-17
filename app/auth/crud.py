from sqlalchemy.orm import Session

from app.database.models import User
from app.auth.schemas import UserRegister
from app.security.password import (
    hash_password,
    verify_password
)

def create_user(db: Session, user: UserRegister):
    """
    Register a new user.
    """

    # Check if username already exists
    existing_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_user:
        raise ValueError(
            "Username already exists"
        )


    # Check if email already exists
    existing_email = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_email:
        raise ValueError(
            "Email already registered"
        )


    # Hash user password
    hashed_password = hash_password(
        user.password
    )


    # Create database user object
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role
    )


    # Save to PostgreSQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return new_user
def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    """
    Verify user login credentials.
    """

    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


    # User does not exist
    if not user:
        return None


    # Verify password
    if not verify_password(
        password,
        user.password_hash
    ):
        return None


    # Login successful
    return user