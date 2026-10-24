from typing import Annotated

from pydantic import BaseModel, Field


class PDFExtracts(BaseModel):
    content: Annotated[list, Field(default_factory=list)]


class PDF_data(BaseModel):
    content: Annotated[list, Field(default_factory=list)]
    content_type: str | None
    filename: str | None
    metadata: dict | None
    size: int