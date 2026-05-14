"""Schémas Pydantic pour les utilisateurs."""

from pydantic import BaseModel, EmailStr

from db.models.user import Role


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None


class UserRead(UserBase):
    id: int
    role: Role
    is_active: bool

    model_config = {"from_attributes": True}
