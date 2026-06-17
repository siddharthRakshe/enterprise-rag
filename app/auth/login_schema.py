from pydantic import BaseModel


class UserLogin(BaseModel):
    """
    Request schema for user login.
    """

    email: str
    password: str


class TokenResponse(BaseModel):
    """
    Response schema after successful login.
    """

    access_token: str
    token_type: str = "bearer"