from datetime import datetime, timedelta, timezone
from fastapi import Response
from core import setting
import jwt
from uuid import uuid4

def create_access_token(user_id: int) -> str:
    isuueTime = datetime.now(timezone.utc)
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "jid": str(uuid4()),
        "token type" : "access",
        "sub": str(user_id),
        "iat" : isuueTime,
        "exp": expire,
    }
    token = jwt.encode(
        payload,
        setting.ACCESS_TOKEN_SECRET_KEY,
        algorithm=setting.ALGORITHM,
    )
    return token

def create_refresh_token(user_id: int) -> str:
    isuTime = datetime.now(timezone.utc)
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=setting.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "jid": str(uuid4()),
        "token type" : "refresh",
        "sub": str(user_id),
        "iat" : isuTime,
        "exp": expire,
    }
    token = jwt.encode(
        payload,
        setting.REFRESH_TOKEN_SECRET_KEY,
        algorithm=setting.ALGORITHM,
    )
    return token

def decode_token(token_type,token: str) -> int:
    if token_type == "access":
        payload = jwt.decode(
            token,
            setting.ACCESS_TOKEN_SECRET_KEY,
            algorithms=[setting.ALGORITHM],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Token subject missing")
        return int(user_id)
    if token_type == "refresh":
            payload = jwt.decode(
                token,
                setting.REFRESH_TOKEN_SECRET_KEY,
                algorithms=[setting.ALGORITHM],
            )
            user_id = payload.get("sub")
            if user_id is None:
                raise ValueError("Token subject missing")
            return int(user_id)

def set_coookie(token_type:str, my_token: str, response: Response)-> None:
    if token_type == "access_token":
        response.set_cookie(
            key=token_type,
            value=my_token,
            httponly=True,
            secure=False, 
            samesite="lax",
            max_age= setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/"
        )
    if token_type == "refresh_token":
            response.set_cookie(
                key=token_type,
                value=my_token,
                httponly=True,
                secure=setting.SECURE_SETTING,
                samesite=setting.SAMESITE_SETTING,
                max_age= setting.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
                path="/"
            )