from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError 

from app.core.database import get_db
from app.core.security import decode_user_token, reusable_oauth

from app.services.user import UserService
from app.repositories.user import UserRepository

from app.repositories.project_access import ProjectAccessRepository

from app.repositories.project import ProjectRepository
from app.services.project import ProjectService

from app.models.user import User

from app.repositories.document import DocumentRepository
from app.services.document import DocumentService
from app.models.document import Document

from app.core.storage.base import StorageService
from app.core.config import settings

from app.core.storage.local import LocalStorageStrategy
from app.core.storage.s3 import S3StorageStrategy

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_user_repo(
        db: Session = Depends(get_db)
) -> UserRepository:
    return UserRepository(db)

def get_project_repo(
        db: Session = Depends(get_db)
) -> ProjectRepository:
    return ProjectRepository(db)

def get_project_access_repo(
        db: Session = Depends(get_db)
) -> ProjectAccessRepository:
    return ProjectAccessRepository(db)

def get_user_service(
        db: Session = Depends(get_db),
        user_repo: UserRepository = Depends(get_user_repo)
) -> UserService:
    return UserService(db, user_repo)

def get_project_service(
        db: Session = Depends(get_db),
        project_repo: ProjectRepository = Depends(get_project_repo),
        project_access_repo: ProjectAccessRepository = Depends(get_project_access_repo)
) -> ProjectService:
    return ProjectService(db, project_repo, project_access_repo)

async def get_current_user(
    token: str = Depends(reusable_oauth),
    user_service: UserService = Depends(get_user_service)
) -> User:
    
    try:
        payload = decode_user_token(token)
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except (JWTError, AttributeError, Exception):
        raise credentials_exception

    user = user_service.get_user_by_email(user_email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    return user

async def get_document_repo(
        db:Session = Depends(get_db)
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
        db: Session = Depends(get_db),
        documents_repo: DocumentRepository = Depends(get_document_repo),
        access_repo: ProjectAccessRepository = Depends(get_project_access_repo),
        storage_service: StorageService = Depends(get_storage_service)
) -> DocumentService:
    return DocumentService(db, documents_repo, access_repo, storage_service) 
