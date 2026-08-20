from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import AuditMixin, IdMixin


class Project(Base, AuditMixin, IdMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    description: Mapped[Text] = mapped_column(
        Text,
        nullable=True,
    )
