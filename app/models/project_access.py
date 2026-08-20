from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import AuditMixin, IdMixin


class ProjectRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"


class ProjectAccess(Base, AuditMixin, IdMixin):
    __tablename__ = "project_access"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "email",
            name="unique_project_user",
        ),
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        ForeignKey("users.email"),
        nullable=False,
    )

    role: Mapped[ProjectRole] = mapped_column(
        SQLAlchemyEnum(ProjectRole),
        nullable=False,
    )

    invited_by: Mapped[str] = mapped_column(
        ForeignKey("users.email"),
        nullable=True,
    )
