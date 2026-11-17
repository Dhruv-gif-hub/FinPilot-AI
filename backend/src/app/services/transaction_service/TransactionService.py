import csv
import io
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_transactions import FinancialTransactions
from app.models.settlement_items import SettlementItem
from app.models.settlements import Settlement

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def decimal_or_none(value: str | None) -> Decimal | None:
    if value is None or not value.strip():
        return None

    return Decimal(value.strip())


def datetime_or_none(value: str | None) -> datetime | None:
    if value is None or not value.strip():
        return None

    return datetime.fromisoformat(value.strip())


async def get_or_create_transaction(
    session: AsyncSession,
    *,
    merchant_id: UUID,
    row: dict,
) -> UUID | None:

    provider_payment_id = (row.get("provider_payment_id") or "").strip()

    if not provider_payment_id:
        return None

    provider = row["provider"].strip().lower()

    statement = (
        insert(FinancialTransactions)
        .values(
            merchant_id=merchant_id,
            provider=provider,
            provider_payment_id=provider_payment_id,
            amount=Decimal(row["amount"]),
            currency=row["currency"].strip().upper(),
            status=row["status"].strip().upper(),
            failure_code=(row.get("failure_code") or "").strip() or None,
            payment_method=row["payment_method"].strip().lower(),
        )
        .on_conflict_do_nothing(
            constraint="uq_financial_transactions_provider_payment"
        )
        .returning(FinancialTransactions.id)
    )

    transaction_id = await session.scalar(statement)

    if transaction_id is not None:
        return transaction_id

    # It already exists: retrieve its ID for the settlement item.
    return await session.scalar(
        select(FinancialTransactions.id).where(
            FinancialTransactions.provider == provider,
            FinancialTransactions.provider_payment_id == provider_payment_id,
        )
    )


async def get_or_create_settlement(
    session: AsyncSession,
    *,
    merchant_id: UUID,
    row: dict,
) -> UUID | None:

    provider_settlement_id = (
        row.get("provider_settlement_id") or ""
    ).strip()

    if not provider_settlement_id:
        return None

    provider = row["provider"].strip().lower()

    statement = (
        insert(Settlement)
        .values(
            merchant_id=merchant_id,
            provider=provider,
            provider_settlement_id=provider_settlement_id,
            currency=row["settlement_currency"].strip().upper(),
            gross_amount=Decimal(row["gross_amount"]),
            fees_amount=Decimal(row["fees_amount"]),
            adjustments_amount=(
                decimal_or_none(row.get("adjustments_amount"))
                or Decimal("0")
            ),
            net_amount=Decimal(row["net_amount"]),
            status=(row.get("settlement_status") or "pending").strip().lower(),
            settled_at=datetime_or_none(row.get("settled_at")),
        )
        .on_conflict_do_nothing(
            constraint="uq_settlements_merchant_provider_settlement"
        )
        .returning(Settlement.id)
    )

    settlement_id = await session.scalar(statement)

    if settlement_id is not None:
        return settlement_id

    # Reuse an existing settlement.
    return await session.scalar(
        select(Settlement.id).where(
            Settlement.merchant_id == merchant_id,
            Settlement.provider == provider,
            Settlement.provider_settlement_id == provider_settlement_id,
        )
    )


async def create_settlement_item(
    session: AsyncSession,
    *,
    settlement_id: UUID,
    transaction_id: UUID | None,
    row: dict,
) -> bool:

    provider_item_id = (row.get("provider_item_id") or "").strip()

    if not provider_item_id:
        return False

    statement = (
        insert(SettlementItem)
        .values(
            settlement_id=settlement_id,
            transaction_id=transaction_id,
            provider_item_id=provider_item_id,
            item_type=row["item_type"].strip().lower(),
            amount=Decimal(row["item_amount"]),
            currency=row["item_currency"].strip().upper(),
        )
        .on_conflict_do_nothing(
            constraint="uq_settlement_items_settlement_provider_item"
        )
        .returning(SettlementItem.id)
    )

    item_id = await session.scalar(statement)

    return item_id is not None


async def import_financial_csv(
    session: AsyncSession,
    *,
    merchant_id: UUID,
    file: UploadFile,
) -> dict:

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="CSV file exceeds the 10 MB limit.",
        )

    try:
        csv_text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV must use UTF-8 encoding.",
        )

    reader = csv.DictReader(io.StringIO(csv_text))

    if not reader.fieldnames:
        raise HTTPException(
            status_code=400,
            detail="CSV file is empty.",
        )

    item_count = 0
    rows_processed = 0

    try:
        for row in reader:

            if not any((value or "").strip() for value in row.values()):
                continue

            rows_processed += 1

            # 1. Create or retrieve transaction.
            transaction_id = await get_or_create_transaction(
                session,
                merchant_id=merchant_id,
                row=row,
            )

            if transaction_id is not None:
                # This counts newly created records, not existing ones.
                # The helper returns an ID in both cases, so use the
                # returned insertion status if exact counts are needed.
                pass

            # 2. Create or retrieve settlement.
            settlement_id = await get_or_create_settlement(
                session,
                merchant_id=merchant_id,
                row=row,
            )

            # 3. Create settlement item if supplied.
            if settlement_id is not None:
                created = await create_settlement_item(
                    session,
                    settlement_id=settlement_id,
                    transaction_id=transaction_id,
                    row=row,
                )

                if created:
                    item_count += 1

        await session.flush()

    except Exception:
        await session.rollback()
        raise

    return {
        "rows_processed": rows_processed,
        "settlement_items_inserted": item_count,
        "message": "CSV import completed.",
    }