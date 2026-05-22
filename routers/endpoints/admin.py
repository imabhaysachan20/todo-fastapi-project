from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from deps import DbSession, require_admin
from models.user import User
from schemas.user import UserCreateAdmin, UserResponse
from services.todo_service import delete_todo, get_todo_by_id
from services.user_service import create_user, delete_user, get_user_by_id

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_as_admin(
    user_in: UserCreateAdmin,
    db: DbSession,
    _: Annotated[User, Depends(require_admin)],
):
    try:
        return create_user(db, user_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        ) from None


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_user(
    user_id: int,
    db: DbSession,
    current_admin: Annotated[User, Depends(require_admin)],
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin cannot delete self")
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    delete_user(db, user)


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_todo(
    todo_id: int,
    db: DbSession,
    _: Annotated[User, Depends(require_admin)],
):
    todo = get_todo_by_id(db, todo_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    delete_todo(db, todo)
