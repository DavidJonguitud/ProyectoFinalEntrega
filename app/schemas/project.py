from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.project_access import ProjectRole


class ProjectCreate(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, description="Nombre del proyecto"
    )
    description: str | None = Field(None, description="Descripción del proyecto")


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class ProjectListResponse(BaseModel):
    project_lis: list[ProjectResponse]


class ProjectInviteRequest(BaseModel):
    user_invited: EmailStr = Field(..., description="Email of the invited user")
    user_role: ProjectRole = Field(..., description="Role assigned")
