from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..schemas.util import ItemType
from .user import Base


class SettlementItem(Base):
    __tablename__ = "settlement_items"

    id: Mapped[UUID] = mapped_column(Uuid,
                                     primary_key=True,  server_default=func.gen_random_uuid())

    settlement_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("FinPilot-AI.settlements.id"),
        nullable=False)

    transaction_id: Mapped[UUID | None] = mapped_column(Uuid, 
                                    ForeignKey("FinPilot-AI.financial_transactions.id"),
        nullable=True)

    provider_item_id: Mapped[str] = mapped_column(String(150), nullable=False,)

    item_type: Mapped[ItemType] = mapped_column(String(30), nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "settlement_id",
            "provider_item_id",
            name="uq_settlement_items_settlement_provider_item",
        ),

        Index(
            "ix_settlement_items_settlement_transaction",
            "settlement_id",
            "transaction_id",
        ),
        
        CheckConstraint(
            "currency ~ '^[A-Z]{3}$'",
            name="ck_settlement_items_currency_format",
        ),
        {"schema": "FinPilot-AI"},
    )