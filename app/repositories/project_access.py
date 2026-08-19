from app.models.project_access import ProjectAccess, ProjectRole
from app.schemas.project_access import ProjectAccessCreate

class ProjectAccessRepository:
    def __init__(self, db):
        self.db = db

    def create_project_access(self, project_access_data: ProjectAccessCreate) -> ProjectAccess:
        project_access = ProjectAccess(
            project_id = project_access_data.project_id,
            email = project_access_data.email,
            role = project_access_data.role,
            invited_by = project_access_data.invited_by
        ) 

        self.db.add(project_access)
        return project_access

    def get_projects_by_user_email(self, user_email: str) -> list[ProjectAccess]:
        return self.db.query(ProjectAccess).filter(
            ProjectAccess.email == user_email
        ).all()

    def get_project_role_by_project_id_and_email(self, project_id: int, email:str) -> ProjectRole:
        access = self.db.query(ProjectAccess).filter(
            ProjectAccess.email == email,
            ProjectAccess.project_id == project_id
        ).first()

        if access:
            return access.role
        return None

    def invite_user_to_project(self, project_id: int, owner_email: str, invited_user_email: str, role: ProjectRole):
        project_access = ProjectAccess(
                project_id = project_id,
                email = invited_user_email,
                role = role,
                invited_by = owner_email
        )

        self.db.add(project_access)
        return project_access