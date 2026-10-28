from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CHAR,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..schemas.util import CaseType, Status
from .user import Base


class ReconciliationCase(Base):
    __tablename__ = "reconciliation_cases"

    id: Mapped[UUID] = mapped_column(Uuid,
                                         primary_key=True,  server_default=func.gen_random_uuid())

    merchant_id: Mapped[UUID] = mapped_column(Uuid,
                                                  ForeignKey("FinPilot-AI.merchants.id"),
                                                          unique=True, nullable=False)

    transaction_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("FinPilot-AI.financial_transactions.id"),
        nullable=True,
    )

    settlement_item_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("FinPilot-AI.settlement_items.id"),
        nullable=True,
    )

    case_type: Mapped[CaseType] = mapped_column(String(40), nullable=False)

    status: Mapped[Status] = mapped_column(String(50), nullable=False)

    expected_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    observed_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    currency: Mapped[str | None] = mapped_column(CHAR(3), nullable=True,)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    resolution_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Case creation time
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Resolution timestamp
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (

        Index(
            "ix_reconciliation_cases_merchant_status_created",
            "merchant_id",
            "status",
            created_at.desc(),
        ),

        # Investigate cases related to a transaction
        Index(
            "ix_reconciliation_cases_transaction_id",
            "transaction_id",
        ),

        # Investigate cases related to a settlement line
        Index(
            "ix_reconciliation_cases_settlement_item_id",
            "settlement_item_id",
        ),
        {"schema": "FinPilot-AI"},
    )