from fastapi import HTTPException,status,Depends,Cookie
from sqlalchemy.orm import Session
from sqlalchemy import exists,or_,and_
from .models import UserModel
from pydantic import EmailStr
from fastapi.security import APIKeyCookie
from auth.jwt_auth import decode_token
from core import get_db
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

cookie_api = APIKeyCookie(
    name="access_token"
)

def check_duplicate_account(
    username: str | None,
    email: EmailStr | None,
    phone_number: str | None,
    db: Session,
    exclude_user_id: int | None = None,
) -> bool:
    duplicate_conditions = []

    if username is not None:
        duplicate_conditions.append(UserModel.username == username)

    if email is not None:
        duplicate_conditions.append(UserModel.email == email)

    if phone_number is not None:
        duplicate_conditions.append(UserModel.phone_number == phone_number)

    if not duplicate_conditions:
        return False

    conditions = [
        or_(*duplicate_conditions),
        UserModel.is_delete == False,
    ]

    if exclude_user_id is not None:
        conditions.append(UserModel.id != exclude_user_id)

    return bool(
        db.query(
            exists().where(and_(*conditions))
        ).scalar()
    )

def find_user(data,db:Session):
    result = db.query(UserModel).where(
        and_(
            or_(
                UserModel.username == data,
                UserModel.email == data,
                UserModel.phone_number == data
                ),
            UserModel.is_delete == False
        )
    ).one_or_none()
    return result


def find_user_by_id(data : int, db : Session) -> str:
    result = db.query(UserModel).where(
        UserModel.id == data
    ).one_or_none()
    
    return result


def get_current_user(
    token = Depends(cookie_api),
    db: Session = Depends(get_db),
):

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login to your account",
        )

    try:
        user_id = decode_token(token_type="access", token=token)

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is expired",
        ) from None

    except (InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from None
    
    user = (
        db.query(
            UserModel.id,
            UserModel.username,
            UserModel.role
        ).where(
            UserModel.id == user_id,
            UserModel.is_delete == False,
            UserModel.is_active == True
        ).one_or_none()
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )
    return user