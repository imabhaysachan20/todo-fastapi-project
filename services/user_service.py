from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from core.security import hash_password
from models.user import User
from schemas.user import UserCreate, UserCreateAdmin


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_username_or_email(db: Session, value: str) -> User | None:
    return db.scalar(select(User).where(or_(User.username == value, User.email == value)))


def create_user(db: Session, user_in: UserCreate | UserCreateAdmin) -> User:
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
        role=getattr(user_in, "role", "normal"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def search_users(db: Session, query: str, current_user_id: int, limit: int = 20) -> list[User]:
    statement = (
        select(User)
        .where(
            User.id != current_user_id,
            User.is_active.is_(True),
            or_(User.username.ilike(f"%{query}%"), User.email.ilike(f"%{query}%")),
        )
        .order_by(User.username)
        .limit(limit)
    )
    return list(db.scalars(statement))


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
