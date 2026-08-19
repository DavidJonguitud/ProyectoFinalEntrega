import logging
import traceback


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from alembic.config import Config
from alembic import command

from app.core.database import create_database_if_not_exists

from app.routers.user import user_router
from app.routers.project import project_router
from app.routers.documents import document_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_if_not_exists()

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
    except Exception as exc:
        print("\n" + "="*50)
        print("Server error")
        traceback.print_exc()
        print("="*50 + "\n")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__}
        )