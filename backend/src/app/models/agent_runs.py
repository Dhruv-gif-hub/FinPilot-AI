from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..schemas.util import Status
from .user import Base


class AgentRuns(Base):
    __tablename__ = "agent_runs"


    id: Mapped[UUID] = mapped_column(Uuid,
                                     primary_key=True,  server_default=func.gen_random_uuid())
    task_id: Mapped[UUID] = mapped_column(Uuid,
                                          ForeignKey("FinPilot-AI.agent_tasks.id"),
                                          unique=True, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[Status] = mapped_column(String(50), nullable=False,
                                                    default=Status.QUEUED)
    worker_id: Mapped[str] = mapped_column(String(150), nullable=True)
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    error_code: Mapped[str] = mapped_column(String(80), nullable=True)
    error_summary: Mapped[str] = mapped_column(String(150), nullable=True)
    model_usage: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())

    __table_args__ = (
        Index(
            "ix_agent_runs_task_attempt_number",
            "task_id",
            attempt_number.desc(),
        ),

        Index(
            "ix_agent_runs_status_started_at",
            "status",
            "started_at",
        ),

        CheckConstraint(
            "attempt_number > 0",
            name="ck_agent_runs_attempt_number_nonnegative",
        ),
        {"schema": "FinPilot-AI"},
        )