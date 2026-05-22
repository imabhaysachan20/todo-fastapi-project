from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from deps import DbSession, require_normal_user
from models.user import User
from schemas.todo import PaginatedTodos, TodoCreate, TodoResponse, TodoShareRequest, TodoShareResponse
from services.todo_service import (
    create_todo,
    delete_todo,
    get_owned_todo,
    list_accessible_todos,
    share_todo,
)
from services.user_service import get_user_by_id

router = APIRouter()


def serialize_todo(todo, current_user_id: int) -> TodoResponse:
    return TodoResponse(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        owner_id=todo.owner_id,
        created_at=todo.created_at,
        shared=todo.owner_id != current_user_id or bool(todo.shared_with),
    )


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_my_todo(
    todo_in: TodoCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(require_normal_user)],
):
    return serialize_todo(create_todo(db, todo_in, current_user), current_user.id)


@router.get("", response_model=PaginatedTodos)
def list_my_todos(
    db: DbSession,
    current_user: Annotated[User, Depends(require_normal_user)],
    search: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
):
    total, items = list_accessible_todos(db, current_user, search, page, size)
    return PaginatedTodos(
        total=total,
        page=page,
        size=size,
        items=[serialize_todo(todo, current_user.id) for todo in items],
    )


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_todo(
    todo_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(require_normal_user)],
):
    todo = get_owned_todo(db, todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    delete_todo(db, todo)


@router.post("/{todo_id}/share", response_model=TodoShareResponse)
def share_my_todo(
    todo_id: int,
    payload: TodoShareRequest,
    db: DbSession,
    current_user: Annotated[User, Depends(require_normal_user)],
):
    todo = get_owned_todo(db, todo_id, current_user.id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    users = []
    for user_id in set(payload.user_ids):
        user = get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )
        users.append(user)

    shared_todo = share_todo(db, todo, users)
    response = serialize_todo(shared_todo, current_user.id).model_dump()
    response["shared_with"] = shared_todo.shared_with
    return response
