from decimal import Decimal
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.reconciliation_cases import ReconciliationCase
from ...schemas.reconciliation import (
    DiscrepancyInput,
    ReconciliationResult,
)
from .ReconciliationRepository import ReconciliationRepository


class ReconciliationService:

    # --------------------------------------------------
    # VALIDATE DISCREPANCY REFERENCES
    # --------------------------------------------------
    @staticmethod
    async def _validate_discrepancy(
        session: AsyncSession,
        *,
        discrepancy: DiscrepancyInput,
        settlement_id: UUID,
        merchant_id: UUID,
    ) -> None:

        if (
            discrepancy.settlement_item_id is None
            and discrepancy.transaction_id is None
        ):
            raise ValueError(
                "A discrepancy must reference a transaction "
                "or settlement item."
            )

        settlement_item = None
        transaction = None

        # Validate settlement item.
        if discrepancy.settlement_item_id is not None:

            settlement_item = (
                await ReconciliationRepository.get_settlement_item(
                    session,
                    discrepancy.settlement_item_id,
                    settlement_id,
                )
            )

            if settlement_item is None:
                raise ValueError(
                    "Settlement item does not belong to this settlement."
                )

        # Validate transaction.
        if discrepancy.transaction_id is not None:

            transaction = (
                await ReconciliationRepository.get_transaction(
                    session,
                    discrepancy.transaction_id,
                    merchant_id,
                )
            )

            if transaction is None:
                raise ValueError(
                    "Transaction does not belong to this merchant."
                )

        # If both records are provided, verify their relationship.
        if (
            settlement_item is not None
            and transaction is not None
            and settlement_item.transaction_id != transaction.id
        ):
            raise ValueError(
                "Settlement item and transaction references "
                "do not match."
            )

        # Ensure the discrepancy currency is well-formed.
        if discrepancy.currency is not None and (
            len(discrepancy.currency) != 3
            or not discrepancy.currency.isalpha()
            or discrepancy.currency != discrepancy.currency.upper()
        ):
                raise ValueError(
                    "Invalid discrepancy currency."
                )

        # Amounts should never be negative in a simple payment
        # reconciliation workflow. If your domain supports negative
        # adjustments, handle those separately.
        for amount in (
            discrepancy.expected_amount,
            discrepancy.observed_amount,
        ):
            if amount is not None and amount < Decimal("0"):
                raise ValueError(
                    "Discrepancy amounts cannot be negative."
                )

    # --------------------------------------------------
    # CREATE RECONCILIATION CASES
    # --------------------------------------------------
    @staticmethod
    async def create_reconciliation_cases(
        session: AsyncSession,
        *,
        merchant_id: UUID,
        reconciliation_data: dict,
    ) -> dict:

        """
        Persist discrepancies already identified by
        the LangChain investigation tools.

        user_id is retained for the application-level
        authorization contract. Merchant membership must
        be verified by the API/worker authorization layer
        before this service is called.
        """

        try:
            reconciliation = ReconciliationResult.model_validate(
                reconciliation_data
            )

        except ValidationError as exc:
            raise ValueError(
                f"Invalid reconciliation result: {exc}"
            ) from exc

        created_cases = []
        existing_cases = []

        async with session.begin():

            # 1. Validate settlement and merchant relationship.
            settlement = (
                await ReconciliationRepository.get_settlement(
                    session,
                    reconciliation.settlement_id,
                    merchant_id,
                )
            )

            if settlement is None:
                raise LookupError(
                    "Settlement not found or access denied."
                )

            # 2. Process identified discrepancies.
            for discrepancy in reconciliation.discrepancies:

                # 3. Validate every database reference.
                await ReconciliationService._validate_discrepancy(
                    session,
                    discrepancy=discrepancy,
                    settlement_id=reconciliation.settlement_id,
                    merchant_id=merchant_id,
                )

                # 4. Check for an existing case.
                existing = (
                    await ReconciliationRepository.get_existing_case(
                        session,
                        settlement_item_id=(
                            discrepancy.settlement_item_id
                        ),
                        transaction_id=(
                            discrepancy.transaction_id
                        ),
                        case_type=discrepancy.case_type,
                    )
                )

                if existing is not None:

                    existing_cases.append(
                        {
                            "case_id": str(existing.id),
                            "case_type": str(existing.case_type),
                            "status": str(existing.status),
                        }
                    )

                    # Never overwrite an existing case,
                    # especially one that is resolved.
                    continue

                # 5. Create a new case.
                case = (
                    await ReconciliationRepository.create_case(
                        session,
                        merchant_id=merchant_id,
                        transaction_id=(
                            discrepancy.transaction_id
                        ),
                        settlement_item_id=(
                            discrepancy.settlement_item_id
                        ),
                        case_type=discrepancy.case_type,
                        status="open",
                        expected_amount=(
                            discrepancy.expected_amount
                        ),
                        observed_amount=(
                            discrepancy.observed_amount
                        ),
                        currency=discrepancy.currency,
                        description=discrepancy.description,
                    )
                )

                created_cases.append(
                    {
                        "case_id": str(case.id),
                        "case_type": str(case.case_type),
                        "status": str(case.status),
                    }
                )

        return {
            "settlement_id": str(reconciliation.settlement_id),
            "total_discrepancies": len(
                reconciliation.discrepancies
            ),
            "created_count": len(created_cases),
            "existing_count": len(existing_cases),
            "created_cases": created_cases,
            "existing_cases": existing_cases,
        }

    # --------------------------------------------------
    # GET RECONCILIATION CASES
    # --------------------------------------------------
    @staticmethod
    async def get_reconciliation_cases(
        session: AsyncSession,
        *,
        merchant_id: UUID,
        settlement_id: UUID | None = None,
    ) -> list[ReconciliationCase]:

        return await ReconciliationRepository.list_cases(
            session,
            merchant_id,
            settlement_id,
        )

    # --------------------------------------------------
    # GET RECONCILIATION SUMMARY
    # --------------------------------------------------
    @staticmethod
    async def get_reconciliation_summary(
        session: AsyncSession,
        *,
        merchant_id: UUID,
        settlement_id: UUID | None = None,
    ) -> dict:

        cases = await ReconciliationService.get_reconciliation_cases(
            session=session,
            merchant_id=merchant_id,
            settlement_id=settlement_id,
        )

        total = len(cases)

        open_count = sum(
            str(case.status).lower() == "pending"
            for case in cases
        )

        resolved_count = sum(
            str(case.status).lower() == "completed"
            for case in cases
        )

        case_breakdown = {}

        for case in cases:

            case_type = str(case.case_type)

            case_breakdown[case_type] = (
                case_breakdown.get(case_type, 0) + 1
            )

        return {
            "total_cases": total,
            "open_cases": open_count,
            "resolved_cases": resolved_count,
            "case_breakdown": case_breakdown,
        }

    # --------------------------------------------------
    # RESOLVE CASE
    # --------------------------------------------------
    @staticmethod
    async def resolve_case(
        session: AsyncSession,
        *,
        case_id: UUID,
        merchant_id: UUID,
        resolution_note: str,
    ) -> UUID:

        if not resolution_note.strip():
            raise ValueError(
                "A resolution note is required."
            )
        async with session.begin():

            case = await ReconciliationRepository.get_case_for_update(
                session,
                case_id,
                merchant_id,
            )

            if case is None:
                raise LookupError(
                    "Reconciliation case not found."
                )

            # Lock the case to prevent concurrent resolution.
            # The repository query should use FOR UPDATE;
            # see the repository improvement below.

            if str(case.status).lower() != "pending":
                raise ValueError(
                    "Only pending cases can be resolved."
                )

            from datetime import datetime, timezone

            await ReconciliationRepository.update_case(
                session,
                case,
                status="completed",
                resolution_note=resolution_note,
                resolved_at=datetime.now(timezone.utc),
            )

            return case.id