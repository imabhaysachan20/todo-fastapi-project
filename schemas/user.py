from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=80)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserCreateAdmin(UserCreate):
    role: str = Field(default="normal", pattern="^(normal|admin)$")


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
