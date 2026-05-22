from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, require_normal_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import search_users

router = APIRouter()


@router.get("/search", response_model=list[UserResponse])
def search_shareable_users(
    db: DbSession,
    current_user: Annotated[User, Depends(require_normal_user)],
    q: str = Query(min_length=1, max_length=80),
    limit: int = Query(default=20, ge=1, le=50),
):
    return search_users(db, q, current_user.id, limit)
