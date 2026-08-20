import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from contextlib import asynccontextmanager

from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from alembic import command
from app.core.config import settings
from app.core.database import create_database_if_not_exists
from app.routers.documents import document_router
from app.routers.project import project_router
from app.routers.user import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_if_not_exists()
    print("\n" + "="*50)
    print(f"ESTRATEGIA DE ALMACENAMIENTO ACTIVA: {settings.STORAGE_STRATEGY}")
    print("="*50 + "\n")

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    print("Application startup complete.")
    yield

    print("Application shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(user_router)
    app.include_router(project_router)
    app.include_router(document_router)
    return app


app = create_app()


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Server error occurred during request processing")

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."},
        )
