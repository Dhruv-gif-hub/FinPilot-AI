
from collections.abc import Sequence
from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel


class GenerationRequest(BaseModel):
    query: str
    title: str

class ReportResponse(TypedDict):
    report: Sequence

class Report(TypedDict):
    task_id: UUID
    status: str
    message: str
    report : dict|None

class Transaction(TypedDict):
    message: str
    result: dict
