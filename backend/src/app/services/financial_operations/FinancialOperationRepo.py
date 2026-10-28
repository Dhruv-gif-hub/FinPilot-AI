from datetime import date
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.financial_transactions import FinancialTransactions
from ...models.settlement_items import SettlementItem
from ...models.settlements import Settlement
from ...models.user_merchants import UserMerchants


class FinancialOperationRepo:

    @staticmethod
    async def get_transactions_for_reconciliation(
        session: AsyncSession,
        merchant_id: UUID,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[FinancialTransactions]:
        
        merchant_access = exists().where(
            UserMerchants.user_id == user_id,
            UserMerchants.merchant_id == merchant_id,
        )
        stmt = (
            select(FinancialTransactions)
            .where(
                FinancialTransactions.merchant_id == merchant_id,
                FinancialTransactions.status == "completed",
                FinancialTransactions.created_at >= start_date,
                FinancialTransactions.created_at < end_date,
                merchant_access
            )
        )

        result = await session.scalars(stmt)
        return list(result.all())

    @staticmethod
    async def get_settlement_items_for_reconciliation(
        session: AsyncSession,
        merchant_id: UUID,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[SettlementItem]:
        
        merchant_access = exists().where(
            UserMerchants.user_id == user_id,
            UserMerchants.merchant_id == merchant_id,
        )
        stmt = (
            select(SettlementItem)
            .join(
                Settlement,
                SettlementItem.settlement_id == Settlement.id,
            )
            .where(
                Settlement.merchant_id == merchant_id,
                Settlement.settled_at >= start_date,
                Settlement.settled_at < end_date,
                merchant_access
            )
        )

        result = await session.scalars(stmt)
        return list(result.all())