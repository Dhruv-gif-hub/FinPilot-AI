from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .user import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[UUID] = mapped_column(Uuid,
                                        primary_key=True,  server_default=func.gen_random_uuid())

    # For example: agent_task.requested
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # ID of the task or other business entity
    aggregate_id: Mapped[UUID] = mapped_column(
        Uuid,
        nullable=False,
    )

    # Identifies one logical event
    deduplication_key: Mapped[str] = mapped_column(
        String(180), unique=True,
        nullable=False,
    )

    # Minimal event payload
    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    # Event creation time
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # When successful publication was recorded
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Number of publication attempts
    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    # Earliest eligible retry time
    next_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Sanitized last publication failure
    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    __table_args__ = (
        # Publication attempts cannot be negative
        CheckConstraint(
            "attempt_count >= 0",
            name="ck_outbox_events_attempt_count_nonnegative",
        ),

        # Find unpublished events eligible for dispatch
        Index(
            "ix_outbox_events_unpublished_next_attempt",
            "next_attempt_at",
            "created_at",
            postgresql_where=text("published_at IS NULL"),
        ),

        # Inspect events belonging to a particular task/entity
        Index(
            "ix_outbox_events_aggregate_created",
            "aggregate_id",
            "created_at",
        ),
        {"schema": "FinPilot-AI"},
    )