from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from .merchant_repo import MerchantSetupRepository


class MerchantSetupService:

    @staticmethod
    async def import_merchants(
        session: AsyncSession,
        *,
        file: UploadFile,
    ):
        return await MerchantSetupRepository.import_merchants_from_csv(
            session=session, file=file
        )

    @staticmethod
    async def add_user_to_merchant(
        session: AsyncSession,
        *,
        user_id: UUID,
    ):
        return await MerchantSetupRepository.add_user_to_all_merchants(
            session=session, user_id=user_id
        )
