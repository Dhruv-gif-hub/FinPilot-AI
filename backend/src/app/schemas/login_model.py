
from typing import Annotated, TypedDict

from fastapi import Form
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Form()]
    password: Annotated[str, Form()]

class SignupResponse(TypedDict):
    message: str
    email: EmailStr

class Logout(TypedDict):
    message: str