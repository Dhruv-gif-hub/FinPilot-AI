from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .user import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(Uuid,
                                        primary_key=True,  server_default=func.gen_random_uuid())

    # User who initiated the action; NULL for system actions
    actor_user_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("FinPilot-AI.users.id"),
        nullable=True,
    )

    # Related merchant, if applicable
    merchant_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("FinPilot-AI.merchants.id"),
        nullable=True,
    )

    # Action performed
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Type of affected resource
    resource_type: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
    )

    # Identifier of the affected resource
    resource_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        nullable=True,
    )

    # Safe contextual metadata; defaults to an empty JSON object
    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    # When the action occurred
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        # User's audit history, newest first
        Index(
            "ix_audit_events_actor_created",
            "actor_user_id",
            created_at.desc(),
        ),

        # Events associated with a particular resource, newest first
        Index(
            "ix_audit_events_resource_created",
            "resource_type",
            "resource_id",
            created_at.desc(),
        ),

        # Merchant's audit history, newest first
        Index(
            "ix_audit_events_merchant_created",
            "merchant_id",
            created_at.desc(),
        ),
        {"schema": "FinPilot-AI"},
    )