
from pydantic import BaseModel


class GenerationRequest(BaseModel):
    query: str
    title: str