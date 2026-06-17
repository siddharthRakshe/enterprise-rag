from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """
    Request schema for user registration.
    """

    username: str
    email: EmailStr
    password: str
    role: str


class UserResponse(BaseModel):
    """
    Response schema after successful registration.
    """

    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True