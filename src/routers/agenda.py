from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.auth.dependencies import get_current_user
from src.database import get_session
from src.models.agenda import Contacto, ContactoCreate, ContactoUpdate
from src.models.user import Usuario

router = APIRouter(prefix="/agenda", tags=["Agenda CRUD"])


@router.get("", response_model=List[Contacto])
def get_contactos(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    return session.exec(select(Contacto).where(Contacto.user_id == current_user.id)).all()


@router.get("/{id}", response_model=Contacto)
def get_contacto(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    contacto = session.get(Contacto, id)

    if not contacto or contacto.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contacto no encontrado")

    return contacto


@router.post("", response_model=Contacto, status_code=status.HTTP_201_CREATED)
def crear_contacto(
    contacto_in: ContactoCreate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    nuevo = Contacto.model_validate(contacto_in)
    nuevo.user_id = current_user.id
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=Contacto)
def actualizar_contacto(
    id: int,
    contacto_in: ContactoUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    contacto_db = session.get(Contacto, id)

    if not contacto_db or contacto_db.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")

    update_data = contacto_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contacto_db, key, value)

    session.add(contacto_db)
    session.commit()
    session.refresh(contacto_db)
    return contacto_db


@router.delete("/{id}")
def eliminar_contacto(
    id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):
    contacto = session.get(Contacto, id)

    if not contacto or contacto.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")

    session.delete(contacto)
    session.commit()
    return {"mensaje": f"Contacto {id} eliminado correctamente por @{current_user.username}"}
