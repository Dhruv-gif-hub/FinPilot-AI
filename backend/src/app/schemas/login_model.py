# backend/src/app/schemas/auth.py

from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: Annotated[EmailStr, Form()]
    password: Annotated[str, Form()]

