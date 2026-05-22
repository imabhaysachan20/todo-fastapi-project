from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum("normal", "admin", name="user_role"), default="normal")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")
    shared_todos = relationship("Todo", secondary="todo_shares", back_populates="shared_with")
