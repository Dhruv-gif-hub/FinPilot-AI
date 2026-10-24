from typing import Annotated

from fastapi import Depends, Security

from ..core.security import get_current_user
from ..services.User.UserFacade import UserRepository
from .redis import redis_client


def get_redis():
    return redis_client    

def get_user_repo(repo: Annotated[UserRepository, Depends()]):
    return repo

def require_read_user():
    return Security(get_current_user, scopes=["read:user"])

def require_write_user():
    return Security(get_current_user, scopes=["write:user"])

def require_delete_user():
    return Security(get_current_user, scopes=["delete:user"])

def require_admin():
    return Security(get_current_user, scopes=["read:user_profile"]) 