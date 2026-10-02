from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from src.auth.security import get_password_hash, verify_password, create_access_token
from src.database import get_session
from src.models.user import Token, Usuario, UsuarioCreate

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=Usuario, status_code=status.HTTP_201_CREATED)
def register(user_data: UsuarioCreate, session: Session = Depends(get_session)):
    existente = session.exec(select(Usuario).where(Usuario.username == user_data.username)).first()

    if existente:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")

    nuevo_usuario = Usuario(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
    )

    session.add(nuevo_usuario)
    session.commit()
    session.refresh(nuevo_usuario)
    return nuevo_usuario


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(Usuario).where(Usuario.username == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
