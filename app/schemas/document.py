from datetime import datetime

from pydantic import BaseModel, Field

from app.models.document import DocumentType


class DocumentBase(BaseModel):
    file_name: str = Field(..., max_length=255, description="Original file name")
    file_type: DocumentType = Field(
        ..., description="File type supported (pdf or docx)"
    )

    model_config = {"from_attributes": True}


class DocumentCreate(DocumentBase):
    project_id: int = Field(..., description="Id of the project")


class DocumentResponse(DocumentBase):
    id: int = Field(..., description="Document unique ID")
    project_id: int = Field(..., description="Associated project id")
    uploaded_by: str = Field(..., description="User email")
    path: str = Field(..., max_length=500, description="File path")

    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class DocumentUpdate(DocumentBase):
    project_id: int = Field(..., description="Id of the project")
