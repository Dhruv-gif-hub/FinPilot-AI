import json
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from ...core.dependencies import get_redis, get_user_repo
from ...schemas.user import signupUser
from .UserFacade import UserRepository


class UserService:
    
    def __init__(self, user_repo : Annotated[UserRepository, Depends(get_user_repo)], 
                redis: Annotated[Redis, Depends(get_redis)]):
        self.user_repo = user_repo
        self.redis = redis

    async def get_user_email(self, email):
        cached = await self.redis.get(f"user_email:{email}")
        if cached:
            data = json.loads(cached)
            return data
        user = await self.user_repo.get_by_email(email = email)
        if user:
            await self.redis.set(
                f"user_email:{email}",
                json.dumps(user.to_dict()),
                ex=3600
            )
        return user

    async def create_user(self, user: signupUser):
        return self.user_repo.create_user(user = user)