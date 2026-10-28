from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from ....models.settlement_items import SettlementItem
from ....services.financial_operations.FinancialOperationService import (
    FinancialOperationService,
)

# Update this value to match the actual ItemType enum value
# used for ordinary payment items in your application.
PAYMENT_ITEM_TYPE = "payment"


def normalize_item_type(item_type) -> str:
    """Support either a string or a Python Enum value."""
    return str(getattr(item_type, "value", item_type)).lower()


def money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


async def reconciliation_discrepancies(
    merchant_id: UUID,
    user_id: UUID,
    start_date: datetime,
    end_date: datetime,
) -> dict:
    if start_date.tzinfo is None or end_date.tzinfo is None:
        raise ValueError("Both dates must include a timezone.")

    if start_date >= end_date:
        raise ValueError("start_date must be earlier than end_date.")

    transactions = await FinancialOperationService.get_transactions_for_reconciliation(
        merchant_id=merchant_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )

    items = await FinancialOperationService.get_settlement_items_for_reconciliation(
        merchant_id=merchant_id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )

    # Separate payment items from fees, refunds, adjustments, etc.
    payment_items = [
        item
        for item in items
        if normalize_item_type(item.item_type) == PAYMENT_ITEM_TYPE
    ]

    items_by_transaction_id: dict[UUID, list[SettlementItem]] = {}

    for item in payment_items:
        if item.transaction_id is not None:
            items_by_transaction_id.setdefault(
                item.transaction_id, []
            ).append(item)

    discrepancies = []
    matched_item_ids: set[UUID] = set()

    for transaction in transactions:
        matches = items_by_transaction_id.get(transaction.id, [])

        if not matches:
            discrepancies.append({
                "discrepancy_type": "missing_settlement_item",
                "transaction_id": str(transaction.id),
                "settlement_item_ids": [],
                "provider_payment_id": transaction.provider_payment_id,
                "expected_amount": str(money(transaction.amount)),
                "observed_amount": None,
                "currency": transaction.currency,
                "variance": None,
                "matching_rationale": (
                    "No payment-type settlement item linked to this "
                    "successful transaction was found in the selected "
                    "settlement period."
                ),
            })
            continue

        if len(matches) > 1:
            discrepancies.append({
                "discrepancy_type": "multiple_settlement_items",
                "transaction_id": str(transaction.id),
                "settlement_item_ids": [
                    str(item.id) for item in matches
                ],
                "provider_payment_id": transaction.provider_payment_id,
                "expected_amount": str(money(transaction.amount)),
                "observed_amount": None,
                "currency": transaction.currency,
                "variance": None,
                "matching_rationale": (
                    "Multiple payment-type settlement items reference "
                    "the same transaction. Verify whether these are "
                    "valid partial settlements or duplicate entries."
                ),
            })

            matched_item_ids.update(item.id for item in matches)
            continue

        item = matches[0]
        matched_item_ids.add(item.id)

        expected_amount = money(transaction.amount)
        observed_amount = money(item.amount)
        variance = observed_amount - expected_amount

        if transaction.currency != item.currency:
            discrepancies.append({
                "discrepancy_type": "currency_mismatch",
                "transaction_id": str(transaction.id),
                "settlement_item_ids": [str(item.id)],
                "provider_payment_id": transaction.provider_payment_id,
                "expected_amount": str(expected_amount),
                "observed_amount": str(observed_amount),
                "expected_currency": transaction.currency,
                "observed_currency": item.currency,
                "variance": None,
                "matching_rationale": (
                    "The linked records have different currencies. "
                    "Their amounts cannot be compared directly."
                ),
            })

        elif variance != Decimal("0.00"):
            discrepancies.append({
                "discrepancy_type": "amount_mismatch",
                "transaction_id": str(transaction.id),
                "settlement_item_ids": [str(item.id)],
                "provider_payment_id": transaction.provider_payment_id,
                "expected_amount": str(expected_amount),
                "observed_amount": str(observed_amount),
                "currency": transaction.currency,
                "variance": str(variance),
                "matching_rationale": (
                    "The linked transaction and payment settlement "
                    "item have different amounts."
                ),
            })

    # Identify payment items that aren't linked to any transaction.
    transaction_ids = {transaction.id for transaction in transactions}

    for item in payment_items:
        if item.id in matched_item_ids:
            continue

        if item.transaction_id is None or item.transaction_id not in transaction_ids:
            discrepancies.append({
                "discrepancy_type": "unlinked_settlement_item",
                "transaction_id": (
                    str(item.transaction_id)
                    if item.transaction_id is not None
                    else None
                ),
                "settlement_item_ids": [str(item.id)],
                "provider_item_id": item.provider_item_id,
                "expected_amount": None,
                "observed_amount": str(money(item.amount)),
                "currency": item.currency,
                "variance": None,
                "matching_rationale": (
                    "This payment settlement item does not link to a "
                    "successful transaction in the selected transaction "
                    "period. It may be orphaned or belong to a transaction "
                    "outside that period."
                ),
            })

    return {
        "merchant_id": str(merchant_id),
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "transactions_checked": len(transactions),
        "settlement_items_checked": len(items),
        "discrepancy_count": len(discrepancies),
        "discrepancies": discrepancies,
        "action_taken": "none",
    }