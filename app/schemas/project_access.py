from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.project_access import ProjectRole


class ProjectAccessCreate(BaseModel):
    project_id: int
    email: EmailStr
    role: ProjectRole
    invited_by: EmailStr | None = None


class ProjectAccessResponse(BaseModel):
    project_id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
