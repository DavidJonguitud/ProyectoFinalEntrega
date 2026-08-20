import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_user_token, reusable_oauth
from app.core.storage.base import StorageService
from app.core.storage.local import LocalStorageStrategy
from app.core.storage.s3 import S3StorageStrategy
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.repositories.project import ProjectRepository
from app.repositories.project_access import ProjectAccessRepository
from app.repositories.user import UserRepository
from app.services.document import DocumentService
from app.services.project import ProjectService
from app.services.user import UserService

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
logger = logging.getLogger(__name__)


def get_user_repo(db: Annotated[Session, Depends(get_db)]) -> UserRepository:
    return UserRepository(db)


def get_project_repo(db: Annotated[Session, Depends(get_db)]) -> ProjectRepository:
    return ProjectRepository(db)


def get_project_access_repo(
    db: Annotated[Session, Depends(get_db)],
) -> ProjectAccessRepository:
    return ProjectAccessRepository(db)


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserService:
    return UserService(db, user_repo)


def get_project_service(
    db: Annotated[Session, Depends(get_db)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repo)],
    project_access_repo: Annotated[
        ProjectAccessRepository, Depends(get_project_access_repo)
    ],
) -> ProjectService:
    return ProjectService(db, project_repo, project_access_repo)


async def get_current_user(
    token: Annotated[str, Depends(reusable_oauth)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:

    try:
        payload = decode_user_token(token)
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except (JWTError, AttributeError) as e:
        raise credentials_exception from e

    except Exception:
        logger.exception("Unexpected system error during token verification")

    user = user_service.get_user_by_email(user_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


async def get_document_repo(
    db: Annotated[Session, Depends(get_db)],
) -> DocumentRepository:
    return DocumentRepository(db)


async def get_storage_service() -> StorageService:
    if settings.STORAGE_STRATEGY == "local":
        return LocalStorageStrategy()
    elif settings.STORAGE_STRATEGY == "s3":
        return S3StorageStrategy()
    else:
        raise ValueError("Invalid Storage Setting")


async def get_document_service(
    db: Annotated[Session, Depends(get_db)],
    documents_repo: Annotated[DocumentRepository, Depends(get_document_repo)],
    access_repo: Annotated[ProjectAccessRepository, Depends(get_project_access_repo)],
    storage_service: Annotated[StorageService, Depends(get_storage_service)],
) -> DocumentService:
    return DocumentService(db, documents_repo, access_repo, storage_service)
