from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..schemas.util import Status
from .user import Base


class AgentApproval(Base):
    __tablename__ = "agent_approvals"

    id: Mapped[UUID] = mapped_column(Uuid,
                                        primary_key=True,  server_default=func.gen_random_uuid())

    task_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("FinPilot-AI.agent_tasks.id"),
            nullable=False,
        )

    # User or actor that requested approval
    requested_by: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("FinPilot-AI.users.id"),
        nullable=False,
    )

    # User who reviewed it, if reviewed
    reviewed_by: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("FinPilot-AI.users.id"),
        nullable=True,
    )

    # Proposed action type
    action_type: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )

    # Exact proposed action and parameters
    action_payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    status: Mapped[Status] = mapped_column(String(50), nullable=False, default=Status.PENDING)

    decision_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Decision time
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (

        Index(
            "ix_agent_approvals_task_status",
            "task_id",
            "status",
        ),

        # Find approvals by status and expiry
        Index(
            "ix_agent_approvals_status_expires_at",
            "status",
            "expires_at",
        ),
        {"schema": "FinPilot-AI"},
    )