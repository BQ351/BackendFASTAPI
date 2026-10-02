import jwt
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr
from sqlmodel import Session, select

from src.auth.security import create_access_token, get_password_hash, verify_password
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from src.database import get_session
from src.models.agenda import Contacto
from src.models.user import Usuario

templates = Jinja2Templates(directory="src/templates")

router = APIRouter(prefix="/views", tags=["Vistas Web (Jinja2)"])


def get_web_user(request: Request, session: Session) -> Usuario | None:
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
    except jwt.PyJWTError:
        return None

    if not username:
        return None
    return session.exec(select(Usuario).where(Usuario.username == username)).first()


def authenticated_redirect(request: Request, username: str) -> RedirectResponse:
    token = create_access_token({"sub": username})
    response = RedirectResponse(url="/views/agenda", status_code=303)
    response.set_cookie(
        "access_token",
        token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/views",
    )
    return response


@router.get("/login")
def render_login_view(request: Request, session: Session = Depends(get_session)):
    if get_web_user(request, session):
        return RedirectResponse(url="/views/agenda", status_code=303)
    return templates.TemplateResponse(request, "access.html", {"mode": "login"})


@router.post("/login")
def login_from_view(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    usuario = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if not usuario or not verify_password(password, usuario.hashed_password):
        return templates.TemplateResponse(
            request,
            "access.html",
            {"mode": "login", "error": "Usuario o contraseña incorrectos"},
            status_code=401,
        )
    return authenticated_redirect(request, usuario.username)


@router.get("/register")
def render_register_view(request: Request, session: Session = Depends(get_session)):
    if get_web_user(request, session):
        return RedirectResponse(url="/views/agenda", status_code=303)
    return templates.TemplateResponse(request, "access.html", {"mode": "register"})


@router.post("/register")
def register_from_view(
    request: Request,
    username: str = Form(..., min_length=3),
    email: EmailStr = Form(...),
    password: str = Form(..., min_length=6),
    session: Session = Depends(get_session),
):
    existing_user = session.exec(select(Usuario).where(Usuario.username == username)).first()
    if existing_user:
        return templates.TemplateResponse(
            request,
            "access.html",
            {"mode": "register", "error": "Ese nombre de usuario ya está registrado"},
            status_code=409,
        )

    usuario = Usuario(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
    )
    session.add(usuario)
    session.commit()
    return authenticated_redirect(request, usuario.username)


@router.post("/logout")
def logout_from_view():
    response = RedirectResponse(url="/views/login", status_code=303)
    response.delete_cookie("access_token", path="/views")
    return response


@router.get("/agenda")
def render_agenda_view(request: Request, session: Session = Depends(get_session)):
    usuario = get_web_user(request, session)
    if not usuario:
        return RedirectResponse(url="/views/login", status_code=303)

    contactos = session.exec(select(Contacto).where(Contacto.user_id == usuario.id)).all()
    return templates.TemplateResponse(
        request,
        "agenda.html",
        {"contactos": contactos, "usuario": usuario},
    )


@router.post("/agenda")
def create_contact_from_form(
    request: Request,
    nombre: str = Form(...),
    telefono: str = Form(...),
    mail: EmailStr = Form(...),
    session: Session = Depends(get_session),
):
    usuario = get_web_user(request, session)
    if not usuario:
        return RedirectResponse(url="/views/login", status_code=303)

    nuevo_contacto = Contacto(nombre=nombre, telefono=telefono, mail=mail, user_id=usuario.id)
    session.add(nuevo_contacto)
    session.commit()
    return RedirectResponse(url="/views/agenda", status_code=303)
