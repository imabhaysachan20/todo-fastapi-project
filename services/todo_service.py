from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from models.todo import Todo, todo_shares
from models.user import User
from schemas.todo import TodoCreate


def create_todo(db: Session, todo_in: TodoCreate, owner: User) -> Todo:
    todo = Todo(title=todo_in.title, description=todo_in.description, owner_id=owner.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def get_todo_by_id(db: Session, todo_id: int) -> Todo | None:
    return db.get(Todo, todo_id)


def get_owned_todo(db: Session, todo_id: int, owner_id: int) -> Todo | None:
    return db.scalar(select(Todo).where(Todo.id == todo_id, Todo.owner_id == owner_id))


def list_accessible_todos(
    db: Session,
    user: User,
    search: str | None,
    page: int,
    size: int,
) -> tuple[int, list[Todo]]:
    shared_subquery = select(todo_shares.c.todo_id).where(todo_shares.c.user_id == user.id)
    statement: Select[tuple[Todo]] = select(Todo).where(
        or_(Todo.owner_id == user.id, Todo.id.in_(shared_subquery))
    )
    if search:
        pattern = f"%{search}%"
        statement = statement.where(or_(Todo.title.ilike(pattern), Todo.description.ilike(pattern)))

    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = list(
        db.scalars(
            statement.order_by(Todo.created_at.desc(), Todo.id.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
    )
    return total, items


def share_todo(db: Session, todo: Todo, users: list[User]) -> Todo:
    existing_ids = {user.id for user in todo.shared_with}
    for user in users:
        if user.id != todo.owner_id and user.id not in existing_ids:
            todo.shared_with.append(user)
    db.commit()
    db.refresh(todo)
    return db.scalar(
        select(Todo).options(selectinload(Todo.shared_with)).where(Todo.id == todo.id)
    ) or todo


def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()
