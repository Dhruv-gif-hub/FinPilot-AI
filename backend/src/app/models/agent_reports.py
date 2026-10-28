from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .user import Base


class AgentReport(Base):
    __tablename__ = "agent_reports"

    id: Mapped[UUID] = mapped_column(Uuid,
                                        primary_key=True,  server_default=func.gen_random_uuid())

    task_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("FinPilot-AI.agent_tasks.id"),
        nullable=False,
    )

    report_version: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String(250), nullable=False,)

    report_type: Mapped[str] = mapped_column(String(40), nullable=False)

    content: Mapped[dict] = mapped_column(JSONB, nullable=False)

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    evidence: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "report_version",
            name="uq_agent_reports_task_version",
        ),

        CheckConstraint(
            "report_version > 0",
            name="ck_agent_reports_version_positive",
        ),

        Index(
            "ix_agent_reports_task_created_at",
            "task_id",
            created_at.desc(),
        ),
        {"schema": "FinPilot-AI"},
    )