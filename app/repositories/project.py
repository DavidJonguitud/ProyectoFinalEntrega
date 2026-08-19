from app.models.project import Project
from app.schemas.project import ProjectCreate

from app.models.project_access import ProjectAccess

class ProjectRepository:
    def __init__(self, db):
        self.db = db


    def create_project(self, project_data: ProjectCreate) -> Project:
        project = Project(
            name = project_data.name,
            description = project_data.description
        )

        self.db.add(project)
        self.db.flush()
        self.db.refresh(project)
        return project

    def update_project(self, project: Project, update_data: dict) -> Project:
        for key, value in update_data.items():
            setattr(project, key, value)
        self.db.add(project)
        return project

    def delete_project(self, project: Project):
        self.db.delete(project)
        self.db.commit()

    def delete_project_accesses(self, project_id: int):
        self.db.query(ProjectAccess).filter(ProjectAccess.project_id == project_id).delete()
        self.db.commit()
    
    def get_project_by_name(self, name: str) -> Project | None:
        return self.db.query(Project).filter(Project.name == name).first()
    
    def get_project_by_id(self, id: int) -> Project | None:
        return self.db.query(Project).filter(Project.id == id).first()

    def get_project_by_id_and_user_email(self, project_id: int, user_email: str) -> Project | None:
        return self.db.query(Project).join(ProjectAccess, ProjectAccess.project_id == Project.id).filter(Project.id == project_id, ProjectAccess.email == user_email).first()  
  
    def get_projects_by_id(self, ids: list[int]) -> list[Project] | None:
        return self.db.query(Project).filter(Project.id.in_(ids)).all()
