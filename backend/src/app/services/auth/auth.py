from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Body, Depends, HTTPException, Response, status
from jwt.exceptions import InvalidTokenError

from app.core.redis import redis_client

from ...core.config import config_value
from ...core.security import create_access_token, create_refresh_token
from ...schemas.auth_model import Token
from ...schemas.login_model import LoginRequest
from ...schemas.user import signupUser
from ..User.UserService import UserService
from .password import password_hash, verify_password

hash_value = password_hash.hash(config_value.HASH_KEY) 

async def authenticate_user(db, email: str, password: str):

    user = await db.get_user_email(email = email)

    if not user:
        verify_password(password, hash_value)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def signup_user(db, user):
    user_in_db = await db.get_user_email(user.email)
    if user_in_db:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    new_user = await db.create_user(user)
    return new_user
    
async def login_access_token(
        form_data: LoginRequest,
        response: Response,
        db : Annotated[UserService, Depends()]
        ):
    user = await authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect username or password , or user is not active"
            )
    user_scopes = config_value.ROLE_SCOPE_MAP.get(user.role, [])
    acces_token_expires = timedelta(minutes=config_value.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email,
              "scope":" ".join(user_scopes)}, expires_delta=acces_token_expires
    )
    refresh_token_expires = timedelta(days=config_value.REFRESH_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
    
    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=config_value.REFRESH_EXPIRE_DAYS * 24 * 60 * 60,
            samesite="lax",
            secure=True
        )
    
    return Token(access_token=access_token, token_type="bearer")

async def signup_access_token(db : Annotated[UserService, Depends()], data : Annotated[signupUser, Body()]): 
    user = await signup_user(db, data)

    return {
        "message": "User created successfully",
        "user_email": user.email
    }

def logout(response: Response, token: str, refresh_token_value: str | None = None):
    now = datetime.now(timezone.utc).timestamp()

    def blocklist_token(raw_token: str) -> None:
        payload = jwt.decode(
            raw_token,
            config_value.SECRET_KEY,
            algorithms=[config_value.ALGORITHM],
        )

        exp_timestamp = payload.get("exp")
        if exp_timestamp is None:
            raise InvalidTokenError("Token has no expiry")

        remaining_time = int(exp_timestamp - now)

        if remaining_time > 0:
            redis_client.set(
                f"blocklist:{raw_token}",
                "logged_out",
                ex=remaining_time,
            )
    response.delete_cookie("refresh_token")

    try:
        payload = jwt.decode(token, config_value.SECRET_KEY, algorithms=[config_value.ALGORITHM])

        if payload.get("token_type") != "access":
            raise InvalidTokenError("Expected access token")

        blocklist_token(token)

        if refresh_token_value:
            blocklist_token(refresh_token_value)
    
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
        secure=True,
    )

    return {"message": "Successfully logged out."}

async def refresh_token(refresh_token_value: str|None, response: Response, db : UserService):
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token",
        )
    
    old_key = f"blocklist:{refresh_token_value}"

    if redis_client.exists(old_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )
    
    try:
        payload = jwt.decode(refresh_token_value, config_value.SECRET_KEY, algorithms=[config_value.ALGORITHM])

        if payload.get("token_type") != "refresh":
            raise InvalidTokenError("Expected refresh token")
        
        email = payload.get("sub")
        exp_timestamp = payload.get("exp")
        if not email or exp_timestamp is None:
            raise InvalidTokenError("Missing token claims")

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    user = await db.get_user_email(email = email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user_scopes = config_value.ROLE_SCOPE_MAP.get(user.role, [])
    acces_token_expires = timedelta(minutes=config_value.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
            data={"sub": user.email,
                  "scope":" ".join(user_scopes)}, expires_delta=acces_token_expires
        )
    new_refresh_token = create_refresh_token(
        data={"sub": user.email},
        expires_delta=timedelta(days=config_value.REFRESH_EXPIRE_DAYS),
    )
    remaining_time = int(exp_timestamp - datetime.now(timezone.utc).timestamp())

    if remaining_time > 0:
        redis_client.set(
            old_key,
            "rotated",
            ex=remaining_time,
        )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=config_value.REFRESH_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=True,
    )

    return Token(access_token=new_access_token, token_type="bearer")