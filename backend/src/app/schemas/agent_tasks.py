from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from .util import TaskType


class AgentTaskCreate(BaseModel):
    merchant_id: UUID

    task_type: TaskType

    prompt: str = Field(
        min_length=5,
        max_length=10_000,
    )

    input_data: dict[str, Any] = Field(
        default_factory=dict,
    )


class AgentTaskCreated(BaseModel):
    task_id: UUID
    status: str
    message: str


class AgentTaskResponse(BaseModel):
    id: UUID
    merchant_id: UUID
    task_type: str
    status: str