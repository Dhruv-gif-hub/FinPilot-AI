
from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, Response

from ..core.middleware.rate_limit import rate_limiter
from ..core.security import oauth2_scheme
from ..schemas.auth_model import Token
from ..schemas.login_model import LoginRequest, Logout, SignupResponse
from ..schemas.user import signupUser
from ..services.auth.auth import (
    login_access_token,
    logout,
    refresh_token,
    signup_access_token,
)
from ..services.User.UserService import UserService

router = APIRouter(prefix="/auth")

login_limiter = rate_limiter(max_requests=5, window_seconds=60)
signup_limiter = rate_limiter(max_requests=3, window_seconds=60)
refresh_limiter = rate_limiter(max_requests=2, window_seconds=60)

@router.post("/token", response_model=Token, dependencies=[Depends(login_limiter)])
async def login(form_data: LoginRequest, response: Response, db : Annotated[UserService, Depends()]
        ):
    return await login_access_token(form_data = form_data, response = response, db = db)

@router.post("/register", response_model=SignupResponse,
              tags=["Sign_Up"], dependencies=[Depends(signup_limiter)])
async def signup(db : Annotated[UserService, Depends()], data : Annotated[signupUser, Body()]):
    return await signup_access_token(db = db, data = data)

@router.post("/logout", response_model=Logout)
def user_logout(response: Response, token: Annotated[str, Depends(oauth2_scheme)], 
     refresh_token_value: Annotated[str | None, Cookie(alias="refresh_token")] = None):
    return logout(response=response, token=token, refresh_token_value=refresh_token_value)

@router.post("/refresh", response_model=Token, dependencies=[Depends(refresh_limiter)])
async def refresh(response: Response,
                  refresh_token_value: Annotated[str|None, Cookie(alias="refresh_token")],
                   db: Annotated[UserService, Depends()]):
    return await refresh_token( refresh_token_value=refresh_token_value, response=response, db = db)