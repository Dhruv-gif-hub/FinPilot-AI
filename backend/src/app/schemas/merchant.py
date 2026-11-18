from typing import Annotated, TypedDict

from fastapi import Form
from pydantic import BaseModel, EmailStr


class MerchantUploadResponse(TypedDict):
    message: str
    result: dict