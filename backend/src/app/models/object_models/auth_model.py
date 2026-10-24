from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str
    scopes: list[str] = Field(default_factory=list)