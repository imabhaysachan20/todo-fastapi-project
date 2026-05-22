from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    owner_id: int
    created_at: datetime
    shared: bool

    model_config = ConfigDict(from_attributes=True)


class TodoShareRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)


class TodoShareResponse(TodoResponse):
    shared_with: list[UserResponse]


class PaginatedTodos(BaseModel):
    total: int
    page: int
    size: int
    items: list[TodoResponse]
