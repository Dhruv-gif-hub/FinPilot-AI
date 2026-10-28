from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from uuid_utils import uuid7

from ..schemas.util import Status, TaskType
from .user import Base


class AgentTask(Base):
    __tablename__ = "agent_tasks"


    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True,  
                                     server_default=func.gen_random_uuid())
    user_id: Mapped[UUID] = mapped_column(Uuid,
                                          ForeignKey("FinPilot-AI.users.id"), nullable=False)
    merchant_id: Mapped[UUID] = mapped_column(Uuid,
                                              ForeignKey("FinPilot-AI.merchants.id"),
                                              nullable=True)
    task_type: Mapped[TaskType] = mapped_column(String(40), nullable=False)
    status: Mapped[Status] = mapped_column(String(50), nullable=False,
                                                    default=Status.QUEUED)
    instruction: Mapped[str] = mapped_column(String, nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid, unique=True, nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    thread_id: Mapped[str] = mapped_column(String(255), unique=True, 
                                           default=lambda: str(uuid7()))
    current_run_id: Mapped[UUID] = mapped_column(Uuid, nullable=True)
    result_summary: Mapped[str] = mapped_column(String, nullable=True)
    error_code: Mapped[str] = mapped_column(String(80), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                   nullable=True)
    cancel_requested_at: Mapped[datetime] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 nullable=True)

    __table_args__ = (UniqueConstraint(
            "user_id",
            "idempotency_key",
            name="uq_agent_tasks_user_idempotency_key",
        ),

        Index(
            "ix_agent_tasks_user_created_at",
            "user_id",
            created_at.desc(),
        ),

        Index(
            "ix_agent_tasks_status_created_at",
            "status",
            "created_at",
        ),
        {"schema": "FinPilot-AI"},
        )