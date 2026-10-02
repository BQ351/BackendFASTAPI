from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import create_db_and_tables
from src.middlewares.timer import response_time_middleware
from src.routers.agenda import router as agenda_router
from src.routers.auth import router as auth_router
from src.routers.views import router as views_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Sistema de Agenda Empresarial",
    description="API Modular con SQLModel, OAuth2/JWT, Middlewares y Jinja2",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(response_time_middleware)

app.include_router(auth_router)
app.include_router(agenda_router)
app.include_router(views_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "docs": "/docs",
        "panel_web": "/views/agenda",
    }
