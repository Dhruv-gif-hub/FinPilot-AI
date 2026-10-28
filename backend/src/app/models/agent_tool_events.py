from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..schemas.util import Status
from .user import Base


class AgentToolEvent(Base):
    __tablename__ = "agent_tool_events"

    id: Mapped[UUID] = mapped_column(Uuid,
                                        primary_key=True,  server_default=func.gen_random_uuid())

    run_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("FinPilot-AI.agent_runs.id"),
        nullable=False,
    )

    # Parent task
    task_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("FinPilot-AI.agent_tasks.id"),
        nullable=False,
    )

    # Sequence number within the run
    event_sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Tool invoked
    tool_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # started, succeeded, failed
    status: Mapped[Status] = mapped_column(
        String(20),
        nullable=False,
    )

    # Redacted, bounded tool arguments
    input_summary: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Redacted, bounded tool result
    output_summary: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Sanitized error category
    error_code: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    # Tool duration in milliseconds
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Event creation time
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        # One sequence number per run
        UniqueConstraint(
            "run_id",
            "event_sequence",
            name="uq_agent_tool_events_run_sequence",
        ),

        # Sequence numbers start at 1
        CheckConstraint(
            "event_sequence > 0",
            name="ck_agent_tool_events_sequence_positive",
        ),

        # Duration must be nonnegative when provided
        CheckConstraint(
            "duration_ms IS NULL OR duration_ms >= 0",
            name="ck_agent_tool_events_duration_nonnegative",
        ),

        Index(
            "ix_agent_tool_events_task_created",
            "task_id",
            "created_at",
        ),
        {"schema": "FinPilot-AI"},
    )