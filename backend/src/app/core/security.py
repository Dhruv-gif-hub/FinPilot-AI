from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError

from app.core.redis import redis_client

from ..models.object_models.auth_model import TokenData
from ..services.User.UserService import UserService
from .config import config_value

# tokenUrl is the endpoint where the client will send the username and password to get the token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token" ,
                                     scopes={
                                         "read:user":"Read User Info",
                                         "write:user":"Modify User Info",
                                         "delete:user":"Delete User"
                                     })
        


def create_access_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy() # to avoid mutating the original data
    if expires_delta:

        expire = datetime.now(timezone.utc) + expires_delta

    else:

        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(to_encode, config_value.SECRET_KEY, algorithm=config_value.ALGORITHM)

    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, config_value.SECRET_KEY, algorithm=config_value.ALGORITHM)
    
    return encoded_jwt

async def get_current_user(security_scopes: SecurityScopes,
 # Security is used to declare that this dependency is required for the endpoint, 
 # and it will use the oauth2_scheme to extract the token from the request.
        token: Annotated[str, Security(oauth2_scheme)],
        request: Request,
        user_access: Annotated[UserService, Depends()]): 
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value}
        )
    redis_key = f"blocklist:{token}"
    if redis_client.exists(redis_key):
        return None

    try:
        payload = jwt.decode(token, config_value.SECRET_KEY, algorithms=[config_value.ALGORITHM])
        if payload.get("token_type") != "access":
            raise credentials_exception
        
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        scope_str = payload.get("scope", "")
        token_scopes = scope_str.split(" ")

        token_data = TokenData(email = email, scopes=token_scopes)

    except InvalidTokenError:
        raise credentials_exception
    
    user = await user_access.get_user_email(email=token_data.email)

    if user is None:
        raise credentials_exception
    for required_scope in security_scopes.scopes:
        if required_scope not in token_data.scopes:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user