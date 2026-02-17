"""SQLAlchemy model for manual debug sessions."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.core.database import Base


class ManualSession(Base):
    """Сессия ручной отладки промптов."""

    __tablename__ = "manual_sessions"

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
        index=True,
    )
    profile_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'active'")
    )
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

    step_runs: Mapped[list["ManualStepRun"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    processor_configs: Mapped[list["ProcessorConfig"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ManualSession(id={self.id}, name={self.name})>"


# Avoid circular imports — these are resolved at runtime
from backend.src.models.manual_step_run import ManualStepRun  # noqa: E402
from backend.src.models.processor_config import ProcessorConfig  # noqa: E402
