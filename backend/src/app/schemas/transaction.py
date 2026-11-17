from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransactionCSVRow(BaseModel):

    model_config = ConfigDict(extra="ignore")

    provider: str = Field(min_length=1, max_length=40)

    provider_payment_id: str = Field(
        min_length=1,
        max_length=150,
    )

    amount: Decimal = Field(
        gt=0,
        max_digits=18,
        decimal_places=2,
    )

    currency: str = Field(
        min_length=3,
        max_length=3,
    )

    status: str

    failure_code: str | None = Field(
        default=None,
        max_length=80,
    )

    payment_method: str = Field(
        min_length=1,
        max_length=40,
    )

    @field_validator("provider", "provider_payment_id", "payment_method")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        return value.strip()

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        value = value.strip().upper()

        if not value.isalpha():
            raise ValueError("Currency must contain three letters")

        return value

    @field_validator("failure_code", mode="before")
    @classmethod
    def normalize_failure_code(cls, value):
        if value is None or not str(value).strip():
            return None

        return str(value).strip() or None

class SettlementCSVRow(BaseModel):
    model_config = ConfigDict(extra="ignore")

    provider_settlement_id: str = Field(
        min_length=1,
        max_length=150,
    )

    settlement_currency: str = Field(
        min_length=3,
        max_length=3,
    )

    gross_amount: Decimal = Field(
        ge=0,
        max_digits=18,
        decimal_places=2,
    )

    fees_amount: Decimal = Field(
        ge=0,
        max_digits=18,
        decimal_places=2,
    )

    adjustments_amount: Decimal = Field(
        max_digits=18,
        decimal_places=2,
    )

    net_amount: Decimal = Field(
        max_digits=18,
        decimal_places=2,
    )

    settlement_status: str = Field(
        default="pending",
        min_length=1,
        max_length=30,
    )

    settled_at: datetime | None = None


class SettlementItemCSVRow(BaseModel):
    model_config = ConfigDict(extra="ignore")

    provider_item_id: str = Field(
        min_length=1,
        max_length=150,
    )

    item_type: str

    item_amount: Decimal = Field(
        max_digits=18,
        decimal_places=2,
    )

    item_currency: str = Field(
        min_length=3,
        max_length=3,
    )

    item_provider_payment_id: str | None = None