"""SQLAlchemy model for student profiles."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.core.database import Base


class StudentProfile(Base):
    """Student profile table - stores uploaded JSON profiles from Phase A."""

    __tablename__ = "student_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    validation_result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<StudentProfile(id={self.id}, topic={self.topic})>"
