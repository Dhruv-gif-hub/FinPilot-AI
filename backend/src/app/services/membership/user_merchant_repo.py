
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_merchants import UserMerchants


class UserMerchantRepository:

    @staticmethod
    async def get_membership(
        session: AsyncSession,
        user_id: UUID,
        merchant_id: UUID,
    ) -> UserMerchants | None:

        stmt = select(UserMerchants).where(
            UserMerchants.user_id == user_id,
            UserMerchants.merchant_id == merchant_id,
        )

        result = await session.scalars(stmt)

        return result.first()

    @staticmethod
    async def has_membership(
        session: AsyncSession,
        user_id: UUID,
        merchant_id: UUID,
    ) -> bool:

        stmt = select(UserMerchants.user_id).where(
            UserMerchants.user_id == user_id,
            UserMerchants.merchant_id == merchant_id,
        ).limit(1)

        result = await session.scalars(stmt)

        return result.first() is not None
