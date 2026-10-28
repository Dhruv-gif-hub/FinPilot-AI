from datetime import date
from uuid import UUID

from sqlalchemy import case, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.financial_transactions import FinancialTransactions
from ...models.user_merchants import UserMerchants


class analytics_repository:

    @staticmethod
    async def get_payment_counts(
        merchant_id: UUID,
        user_id: UUID,
        start_date: date,
        end_date: date,
        session: AsyncSession
    ):
        
        merchant_access = exists().where(
            UserMerchants.user_id == user_id,
            UserMerchants.merchant_id == merchant_id,
        )

        stmt = select(
            func.count(FinancialTransactions.id).label("total_payments"),

            func.count(
                case(
                    (FinancialTransactions.status == "completed", 1)
                )
            ).label("successful_payments"),

            func.count(
                case(
                    (FinancialTransactions.status == "failed", 1)
                )
            ).label("failed_payments"),
        ).where(
            FinancialTransactions.merchant_id == merchant_id,
            FinancialTransactions.created_at >= start_date,
            FinancialTransactions.created_at < end_date,
            merchant_access
        )
        result = await session.execute(stmt)
        row = result.one()
        
        return {
        "total_payments": row.total_payments,
        "successful_payments": row.successful_payments,
        "failed_payments": row.failed_payments
    }

    @staticmethod
    async def get_failures_by_category(
        merchant_id: UUID,
        user_id: UUID,
        start_date: date,
        end_date: date,
        session: AsyncSession,
    ) -> dict:
        
        merchant_access = exists().where(
            UserMerchants.user_id == user_id,
            UserMerchants.merchant_id == merchant_id,
        )
        stmt = (
            select(
                FinancialTransactions.failure_code,
                func.count(FinancialTransactions.id).label("failure_count"),
            )
            .where(
                FinancialTransactions.merchant_id == merchant_id,
                FinancialTransactions.status == "failed",
                FinancialTransactions.created_at >= start_date,
                FinancialTransactions.created_at < end_date,
                merchant_access
            )
            .group_by(FinancialTransactions.failure_code)
        )

        result = await session.execute(stmt)

        return {
            failure_code: count
            for failure_code, count in result.all()
        }