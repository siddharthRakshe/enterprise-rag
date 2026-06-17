from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func

from app.database.connection import Base


class User(Base):
    """
    User table model
    """

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        Text,
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )