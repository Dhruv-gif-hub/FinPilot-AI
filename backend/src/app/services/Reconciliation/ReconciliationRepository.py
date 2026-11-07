from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.financial_transactions import FinancialTransactions
from ...models.reconciliation_cases import ReconciliationCase
from ...models.settlement_items import SettlementItem
from ...models.settlements import Settlement


class ReconciliationRepository:

    # --------------------------------------------------
    # SETTLEMENT
    # --------------------------------------------------
    @staticmethod
    async def get_settlement(
        session: AsyncSession,
        settlement_id: UUID,
        merchant_id: UUID,
    ) -> Settlement | None:

        stmt = select(Settlement).where(
            Settlement.id == settlement_id,
            Settlement.merchant_id == merchant_id,
        )

        result = await session.scalars(stmt)

        return result.first()

    # --------------------------------------------------
    # SETTLEMENT ITEMS
    # --------------------------------------------------

    @staticmethod
    async def get_settlement_item(
        session: AsyncSession,
        settlement_item_id: UUID,
        settlement_id: UUID,
    ) -> SettlementItem | None:

        stmt = select(SettlementItem).where(
            SettlementItem.id == settlement_item_id,
            SettlementItem.settlement_id == settlement_id,
        )

        result = await session.scalars(stmt)

        return result.first()

    @staticmethod
    async def get_settlement_items(
        session: AsyncSession,
        settlement_id: UUID,
    ) -> list[SettlementItem]:

        stmt = select(SettlementItem).where(
            SettlementItem.settlement_id == settlement_id
        )

        result = await session.scalars(stmt)

        return list(result.all())

    # --------------------------------------------------
    # FINANCIAL TRANSACTIONS
    # --------------------------------------------------
    @staticmethod
    async def get_transaction(
        session: AsyncSession,
        transaction_id: UUID,
        merchant_id: UUID,
    ) -> FinancialTransactions | None:

        stmt = select(FinancialTransactions).where(
            FinancialTransactions.id == transaction_id,
            FinancialTransactions.merchant_id == merchant_id,
        )

        result = await session.scalars(stmt)

        return result.first()

    # --------------------------------------------------
    # EXISTING RECONCILIATION CASE
    # --------------------------------------------------
    @staticmethod
    async def get_existing_case(
        session: AsyncSession,
        *,
        settlement_item_id: UUID | None,
        transaction_id: UUID | None,
        case_type: str,
    ) -> ReconciliationCase | None:

        stmt = select(ReconciliationCase).where(
            ReconciliationCase.case_type == case_type
        )

        if settlement_item_id is not None:
            stmt = stmt.where(
                ReconciliationCase.settlement_item_id
                == settlement_item_id
            )

        elif transaction_id is not None:
            stmt = stmt.where(
                ReconciliationCase.transaction_id == transaction_id,
                ReconciliationCase.settlement_item_id.is_(None),
            )

        else:
            raise ValueError(
                "A settlement item ID or transaction ID is required."
            )

        result = await session.scalars(stmt)

        return result.first()

    # --------------------------------------------------
    # CREATE CASE
    # --------------------------------------------------

    @staticmethod
    async def create_case(
        session: AsyncSession,
        **kwargs,
    ) -> ReconciliationCase:

        case = ReconciliationCase(**kwargs)

        session.add(case)

        await session.flush()

        await session.commit()

        return case

    # --------------------------------------------------
    # LIST CASES
    # --------------------------------------------------
    @staticmethod
    async def list_cases(
        session: AsyncSession,
        merchant_id: UUID,
        settlement_id: UUID | None = None,
    ) -> list[ReconciliationCase]:

        stmt = select(ReconciliationCase).where(
            ReconciliationCase.merchant_id == merchant_id
        )

        if settlement_id is not None:
            stmt = (
                stmt.join(
                    SettlementItem,
                    ReconciliationCase.settlement_item_id
                    == SettlementItem.id,
                )
                .where(
                    SettlementItem.settlement_id == settlement_id
                )
            )

        stmt = stmt.order_by(
            ReconciliationCase.created_at.desc()
        )

        result = await session.scalars(stmt)

        return list(result.all())

    # --------------------------------------------------
    # GET CASE
    # --------------------------------------------------
    @staticmethod
    async def get_case_for_update(
        session: AsyncSession,
        case_id: UUID,
        merchant_id: UUID,
    ) -> ReconciliationCase | None:

        stmt = select(ReconciliationCase).where(
            ReconciliationCase.id == case_id,
            ReconciliationCase.merchant_id == merchant_id,
        ).with_for_update()

        result = await session.scalars(stmt)

        return result.first()

    # --------------------------------------------------
    # UPDATE CASE
    # --------------------------------------------------
    @staticmethod
    async def update_case(
        session: AsyncSession,
        case: ReconciliationCase,
        **kwargs,
    ) -> ReconciliationCase:

        for key, value in kwargs.items():
            setattr(case, key, value)

        await session.flush()

        await session.commit()

        return case