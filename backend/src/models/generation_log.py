"""SQLAlchemy model for generation logs."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, TIMESTAMP, Float, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from backend.src.core.database import Base


class GenerationLog(Base):
    """Generation log table - stores intermediate pipeline step results for debugging."""

    __tablename__ = "generation_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    track_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personalized_tracks.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_name: Mapped[str] = mapped_column(String(50), nullable=False)
    step_output: Mapped[dict] = mapped_column(JSONB, nullable=False)
    llm_calls: Mapped[list] = mapped_column(ARRAY(JSONB), nullable=False)
    step_duration_sec: Mapped[float] = mapped_column(Float, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    def __repr__(self) -> str:
        return f"<GenerationLog(track_id={self.track_id}, step={self.step_name})>"
