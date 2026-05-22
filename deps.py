from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.security import decode_access_token
from db.session import get_db
from models.user import User
from services.user_service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

DbSession = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(db: DbSession, token: TokenDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (jwt.PyJWTError, TypeError, ValueError):
        raise credentials_exception from None

    user = get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise credentials_exception
    return user


def require_normal_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != "normal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Normal user required")
    return current_user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin user required")
    return current_user
