"""
SQLAlchemy модель для логов генерации треков.

Хранит детальные логи выполнения каждого шага pipeline B1-B8.
"""

import uuid
from datetime import datetime

from sqlalchemy import UUID, JSONB, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.core.database import Base


class GenerationLog(Base):
    """
    Модель лога выполнения шага pipeline.

    Attributes:
        id: UUID первичный ключ
        track_id: FK на personalized_tracks
        step_name: Название шага (B1, B2, ..., B8)
        step_output: JSONB результат шага
        llm_calls: JSONB массив LLM вызовов (промпт, ответ, токены)
        step_duration_sec: Длительность шага в секундах
        error_message: Текст ошибки (если шаг упал)
        created_at: Timestamp создания записи
    """

    __tablename__ = "generation_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    track_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("personalized_tracks.id", ondelete="CASCADE"),
        nullable=False,
    )

    step_name: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Название шага: B1, B2, ..., B8",
    )

    step_output: Mapped[dict] = mapped_column(
        JSONB,
        nullable=True,
        comment="Результат выполнения шага (Pydantic schema → dict)",
    )

    llm_calls: Mapped[list] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Массив LLM вызовов: [{prompt, response, tokens, duration}]",
    )

    step_duration_sec: Mapped[float] = mapped_column(
        Integer,
        nullable=True,
        comment="Длительность шага в секундах",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Текст ошибки если шаг упал",
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    track: Mapped["PersonalizedTrack"] = relationship(
        "PersonalizedTrack",
        back_populates="logs",
    )

    # Indexes
    __table_args__ = (
        Index(
            "ix_generation_logs_track_step",
            "track_id",
            "step_name",
            unique=False,
        ),
    )

    def __repr__(self) -> str:
        """Строковое представление."""
        return f"<GenerationLog(track_id={self.track_id}, step={self.step_name})>"
