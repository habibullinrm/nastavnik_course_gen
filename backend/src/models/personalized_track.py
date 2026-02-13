"""SQLAlchemy model for personalized tracks."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, TIMESTAMP, Float, Integer, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.core.database import Base


class PersonalizedTrack(Base):
    """Personalized track table - stores generated course tracks from pipeline B1-B8."""

    __tablename__ = "personalized_tracks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    qa_report_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qa_reports.id", ondelete="SET NULL"),
        nullable=True,
    )
    track_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generation_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(50), nullable=False)
    validation_b8: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    generation_duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    batch_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.utcnow,
    )

    # Relationships
    logs: Mapped[list["GenerationLog"]] = relationship(
        "GenerationLog",
        back_populates="track",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PersonalizedTrack(id={self.id}, status={self.status})>"
