
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .user_merchant_repo import UserMerchantRepository


class MerchantMembershipService:

    @staticmethod
    async def verify_merchant_access(
        session: AsyncSession,
        user_id: UUID,
        merchant_id: UUID,
    ) -> None:

        membership = await UserMerchantRepository.get_membership(
            session=session,
            user_id=user_id,
            merchant_id=merchant_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this merchant.",
            )

    @staticmethod
    async def get_user_merchant_role(
        session: AsyncSession,
        user_id: UUID,
        merchant_id: UUID,
    ):

        membership = await UserMerchantRepository.get_membership(
            session=session,
            user_id=user_id,
            merchant_id=merchant_id,
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this merchant.",
            )

        return membership.role
