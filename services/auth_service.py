from datetime import timedelta

from sqlalchemy.orm import Session

from core.config import settings
from core.security import create_access_token, verify_password
from models.user import User
from services.user_service import get_user_by_username_or_email


def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    user = get_user_by_username_or_email(db, username_or_email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def issue_access_token(user: User) -> str:
    return create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
