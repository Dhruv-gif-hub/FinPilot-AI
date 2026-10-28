from datetime import date
from uuid import UUID

from ...db.session import Session_local
from .FinancialOperationRepo import FinancialOperationRepo


class FinancialOperationService:

    @staticmethod
    async def get_transactions_for_reconciliation(
        merchant_id: UUID,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ):
        async with Session_local() as session:
            return await FinancialOperationRepo.get_transactions_for_reconciliation(
                merchant_id=merchant_id, user_id=user_id, start_date=start_date,
                end_date=end_date, session=session
            )

    @staticmethod
    async def get_settlement_items_for_reconciliation(
        merchant_id: UUID,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ):
        async with Session_local() as session:
            return await FinancialOperationRepo.get_settlement_items_for_reconciliation(
                merchant_id=merchant_id, user_id=user_id, start_date=start_date,
                end_date=end_date, session=session
            )