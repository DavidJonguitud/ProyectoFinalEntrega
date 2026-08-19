import os
import uuid
import logging
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.document import Document
from app.repositories.document import DocumentRepository
from app.repositories.project_access import ProjectAccessRepository
from app.schemas.document import DocumentType, DocumentUpdate
from app.schemas.project import ProjectRole
from app.core.storage.base import StorageService

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self, 
        db: Session, 
        document_repo: DocumentRepository, 
        access_repo: ProjectAccessRepository, 
        storage_service: StorageService
    ):
        self.db = db
        self.document_repo = document_repo
        self.access_repo = access_repo
        self.storage_service = storage_service

    async def get_project_documents(self, project_id: int, user_email: str) -> list[Document]:
        access = self.access_repo.get_project_role_by_project_id_and_email(project_id, user_email)
        if not access:
            raise ValueError("The project does not exist or you do not have permission to access.")
        return self.document_repo.get_documents_by_project_id(project_id)

    async def upload_document_for_project(
        self,
        project_id: int,
        file: UploadFile,
        current_user: User
    ) -> Document:
        access = self.access_repo.get_project_role_by_project_id_and_email(project_id, current_user.email)
        if not access:
            raise ValueError("The project does not exist or you do not have permission to access.")

        if access not in [ProjectRole.OWNER, ProjectRole.MEMBER]:
            raise PermissionError("Only members or owner can upload documents.")

        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        try:
            document_type = DocumentType(file_ext)
        except ValueError:
            raise ValueError(f"Unsupported file type '{file_ext}'. Only PDF and DOCX are allowed.")

        file_path = await self.storage_service.upload_file(
            file=file,
            folder=f"project_{project_id}"
        )

        return self.document_repo.create_document(
            project_id=project_id,
            uploaded_by=current_user.email,
            file_name=file.filename,
            file_type=document_type,
            path=file_path
        )

    async def get_document_path_for_download(self, document_id: int, current_user: User) -> tuple[str, str]:
        document = self.document_repo.get_document_by_id(document_id)
        if not document:
            raise ValueError("The document does not exist")

        access = self.access_repo.get_project_role_by_project_id_and_email(document.project_id, current_user.email)
        if not access:
            raise PermissionError("You do not have permission to access the project of this document")

        file_source = await self.storage_service.get_file_for_download(document.path)

        return file_source, document.file_name

    async def update_project_for_authorized_user(self, document_id: int, current_user: User, file: UploadFile) -> Document:
        document = self.document_repo.get_document_by_id(document_id)
        if not document:
            raise ValueError("The document does not exist.")

        old_file_path = document.path

        access = self.access_repo.get_project_role_by_project_id_and_email(document.project_id, current_user.email)
        if not access:
            raise PermissionError("You do not have permission to access this project.")

        if access not in [ProjectRole.OWNER, ProjectRole.MEMBER]:
            raise PermissionError("Only members or owner can update documents.")

        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        try:
            document_type = DocumentType(file_ext)
        except ValueError:
            raise ValueError(f"Unsupported file type '{file_ext}'. Only PDF and DOCX are allowed")

        new_file_path = await self.storage_service.upload_file(
            file=file,
            folder=f"project_{document.project_id}"
        )

        try:
            if old_file_path:
                await self.storage_service.delete_file(old_file_path)
        except Exception as e:
            logger.warning(f"Could not delete old file {old_file_path}: {e}")

        update_metadata = {
            "file_name": file.filename,
            "file_type": document_type,
            "path": new_file_path,
            "uploaded_by": current_user.email
        }

        return self.document_repo.update_document(document, update_metadata)

    async def delete_project_for_authorized_user(self, document_id: int, current_user: User):
        document = self.document_repo.get_document_by_id(document_id)
        if not document:
            raise ValueError("The document does not exist.")

        old_file_path = document.path

        access = self.access_repo.get_project_role_by_project_id_and_email(document.project_id, current_user.email)
        if not access:
            raise PermissionError("You do not have permission to access this project.")

        if access not in [ProjectRole.OWNER, ProjectRole.MEMBER]:
            raise PermissionError("Only members or owner can update documents.")

        self.document_repo.delete_document(document)
        
        try:
            if old_file_path:
                await self.storage_service.delete_file(old_file_path)
        except Exception as e:
            logger.warning(f"Could not delete old file {old_file_path}: {e}")