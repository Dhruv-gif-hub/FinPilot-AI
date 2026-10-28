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

from ..schemas.util import Status
from .user import Base


class FinancialTransactions(Base):
    __tablename__ = "financial_transactions"

    id: Mapped[UUID] = mapped_column(Uuid,
                                     primary_key=True,  server_default=func.gen_random_uuid())
    merchant_id: Mapped[UUID] = mapped_column(Uuid,
                                              ForeignKey("FinPilot-AI.merchants.id"),
                                                  unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    provider_payment_id: Mapped[str] = mapped_column(String(150), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    status: Mapped[Status] = mapped_column(String(50), nullable=False,
                                                        default=Status.QUEUED)
    failure_code: Mapped[str] = mapped_column(String(80), nullable=True)
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_payment_id",
            name="uq_financial_transactions_provider_payment",
        ),
            CheckConstraint(
            "amount > 0",
            name="ck_financial_transactions_amount_nonnegative",
        ),
            Index(
            "ix_financial_transactionss_merchant_created_at",
            "merchant_id",
            created_at.desc(),
        ),
            Index(
            "ix_financial_transactionss_merchant_status_created_at",
            "merchant_id",
            "status",
            created_at.desc(),
        ),
        {"schema": "FinPilot-AI"},
    )