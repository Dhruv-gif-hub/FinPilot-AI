from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.db_instance import get_db
from ...models.user import User
from ...schemas.user import signupUser
from ...services.auth.password import get_password_hash
from ..Merchant.merchantservice import MerchantSetupService


class UserRepository:

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_db)]
    ):
        self.session = session

    async def get_by_email(self, email):
        stmt = select(User).where(User.email == email)
        result = await self.session.scalars(stmt)
        return result.first()

    async def create_user(self, user: signupUser):
        hashed_password = get_password_hash(user.password)
        created_user = User(
            username=user.username,
            password=hashed_password,
            email=user.email
        )
        self.session.add(created_user)
        await self.session.flush()

        added_user_to_merchant = await MerchantSetupService.add_user_to_merchant(
            session=self.session, user_id=created_user.id
        )
        return created_user 