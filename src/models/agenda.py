import re
from typing import Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


class ContactoBase(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    telefono: str = Field(min_length=7, max_length=15)
    mail: EmailStr

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, value: str) -> str:
        if not re.fullmatch(r"\d{7,15}", value):
            raise ValueError("El teléfono debe contener solo números y tener entre 7 y 15 dígitos")
        return value


class Contacto(ContactoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="usuario.id")


class ContactoCreate(ContactoBase):
    pass


class ContactoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=50)
    telefono: Optional[str] = Field(default=None, min_length=7, max_length=15)
    mail: Optional[EmailStr] = None

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not re.fullmatch(r"\d{7,15}", value):
            raise ValueError("El teléfono debe contener solo números y tener entre 7 y 15 dígitos")
        return value
