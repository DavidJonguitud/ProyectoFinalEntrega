import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import DatabaseTransactionError
from app.models.project import Project
from app.models.project_access import ProjectRole
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.project_access import ProjectAccessRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.project_access import ProjectAccessCreate

logger = logging.getLogger(__name__)


class ProjectService:
    def __init__(
        self,
        db: Session,
        project_repo: ProjectRepository,
        project_access_repo: ProjectAccessRepository,
    ):
        self.db = db
        self.project_repo = project_repo
        self.project_access_repo = project_access_repo

    async def create_project(self, project_data: ProjectCreate, owner: User) -> Project:
        if (
            self.project_repo.get_project_by_name(project_data.name) is not None
        ):  # mockear para test unitario de servicio -> con exito y con error
            logger.warning("A project with that name already exists")
            raise ValueError("A project with that name already exists")

        try:
            project = self.project_repo.create_project(
                project_data
            )  # mockear y validar llamadas

            self.db.flush()

            access_payload = ProjectAccessCreate(
                project_id=project.id,
                email=owner.email,
                role=ProjectRole.OWNER,
                invited_by=None,
            )

            self.project_access_repo.create_project_access(access_payload)  # mockear

            self.db.commit()
            self.db.refresh(project)
            logger.info(
                f"Project '{project.name}' successfully created by user '{owner.email}'"
            )
            return project

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Transaction failed, rolling back changes. Error: {e}")
            raise DatabaseTransactionError(
                f"Could not create project and assign owner: {e}"
            )

    async def update_project_for_authorized_user(
        self, project_id: int, update_data: ProjectUpdate, user: User
    ) -> Project:
        project = self.project_repo.get_project_by_id_and_user_email(
            project_id, user.email
        )

        if not project:
            raise ValueError(
                "The project does not exist or you do not have permission to access it."
            )

        data_to_update = update_data.model_dump(exclude_unset=True)
        if not data_to_update:
            raise ValueError("No fields provided for update")

        updated_project = self.project_repo.update_project(project, data_to_update)
        self.db.commit()
        self.db.refresh(updated_project)
        return updated_project

    async def get_project_by_id_for_authorized_user(
        self, id: int, user_email: User
    ) -> Project:
        project = self.project_repo.get_project_by_id_and_user_email(id, user_email)
        if not project:
            raise ValueError(
                "The project does not exist or you do not have permission to access it."
            )

        return project

    async def get_projects_by_user(self, current_user: User) -> list[Project]:
        accesses = self.project_access_repo.get_projects_by_user_email(
            current_user.email
        )
        if not accesses:
            return []

        project_ids = [access.project_id for access in accesses]
        return self.project_repo.get_projects_by_id(project_ids)

    async def delete_project_for_authorized_owner(
        self, project_id: int, current_user: User
    ):
        project = self.project_repo.get_project_by_id_and_user_email(
            project_id, current_user.email
        )
        role = self.project_access_repo.get_project_role_by_project_id_and_email(
            project_id, current_user.email
        )
        if project and role == ProjectRole.OWNER:
            self.project_repo.delete_project_accesses(project_id)
            self.project_repo.delete_project(project)

    async def invite_user_to_project(
        self, project_id: int, owner: User, invited_user: str, role: ProjectRole
    ):
        access = self.project_access_repo.get_project_role_by_project_id_and_email(
            project_id, owner.email
        )
        project = self.project_repo.get_project_by_id_and_user_email(
            project_id, owner.email
        )
        if not access:
            raise ValueError(
                "The project does not exist or you do not have permission to access it."
            )
        if access != ProjectRole.OWNER:
            raise ValueError("Only the owner of the project can invite users to it.")
        if project and access == ProjectRole.OWNER:
            invite = self.project_access_repo.invite_user_to_project(
                project_id, owner.email, invited_user, role
            )
            self.db.commit()
            self.db.refresh(invite)
            return invite

    # async def invite_user_to_project_by_email(
    #     self, project_id: int, email: str, current_user: User
    # ):
    #     project = self.project_repo.get_project_by_id(project_id)
    #     if project is None:
    #         raise ValueError(
    #             "The project does not exist or you do not have permission to access it."
    #         )

    #     access = self.project_access_repo.get_project_role_by_project_id_and_email(
    #         project_id, current_user.email
    #     )

    #     if access != ProjectRole.OWNER:
    #         raise ValueError("Only the owner of the project can invite users to it.")

    #     jwt_invitation_token = create_project_invitation_token(
    #         project_id=project_id, invited_email=email
    #     )

    # url = urlunparse("http://127.0.0.1:8000/join?token=", jwt_invitation_token)
