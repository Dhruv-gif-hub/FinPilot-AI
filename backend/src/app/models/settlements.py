from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .user import Base


class Settlement(Base):
    __tablename__ = "settlements"

    # Internal settlement ID
    id: Mapped[UUID] = mapped_column(Uuid,
                                     primary_key=True,  server_default=func.gen_random_uuid())
    merchant_id: Mapped[UUID] = mapped_column(Uuid,
                                              ForeignKey("FinPilot-AI.merchants.id"),
                                                      unique=True, nullable=False)

    provider: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    provider_settlement_id: Mapped[str] = mapped_column(String(150), nullable=False,)

    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)

    gross_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    fees_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    adjustments_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), 
                                                        nullable=False,server_default=text("0"))

    net_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    status: Mapped[str] = mapped_column(String(30), 
                                        nullable=False, server_default=text("'pending'"))

    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "gross_amount >= 0",
            name="ck_settlements_gross_amount_nonnegative",
        ),
        CheckConstraint(
            "fees_amount >= 0",
            name="ck_settlements_fees_amount_nonnegative",
        ),
        CheckConstraint(
            "currency ~ '^[A-Z]{3}$'",
            name="ck_settlements_currency_format",
        ),
        {"schema": "FinPilot-AI"},
    )