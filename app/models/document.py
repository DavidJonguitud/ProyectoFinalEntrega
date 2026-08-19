from enum import Enum

from sqlalchemy import Integer, String, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

from app.models.base import AuditMixin, IdMixin

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"

class Document(Base, AuditMixin, IdMixin):
    __tablename__= "documents"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        index=True,
        nullable=False,
    )

    uploaded_by: Mapped[str] = mapped_column(
        ForeignKey("users.email"),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_type: Mapped[DocumentType] = mapped_column(
        SQLAlchemyEnum(DocumentType),
        nullable=False,
    )

    path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )