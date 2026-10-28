from datetime import date
from uuid import UUID

from ...db.session import Session_local
from .analytics_repository import analytics_repository


class analytics_service:

    @staticmethod
    async def get_payment_counts(
        merchant_id: UUID,
        user_id: UUID,
        start_date: date,
        end_date: date,
    ):
        async with Session_local() as session:
            return await analytics_repository.get_payment_counts(
                merchant_id=merchant_id, user_id=user_id, start_date=start_date, end_date=end_date,
                session=session
            )

    @staticmethod
    async def get_failures_by_category(
            merchant_id: UUID,
            user_id: UUID,
            start_date: date,
            end_date: date
        ) -> dict:
        async with Session_local() as session:
            return await analytics_repository.get_failures_by_category(
                merchant_id=merchant_id, user_id=user_id, start_date=start_date,
                end_date=end_date, session=session
            )