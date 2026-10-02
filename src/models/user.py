from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, min_length=3)
    email: EmailStr
    hashed_password: str


class UsuarioCreate(SQLModel):
    username: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=6)


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
