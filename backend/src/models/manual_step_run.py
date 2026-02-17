"""SQLAlchemy model for manual step runs."""

import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, Integer, String, Text, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.core.database import Base


class ManualStepRun(Base):
    """Полный снимок запуска шага в ручном режиме."""

    __tablename__ = "manual_step_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("manual_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_name: Mapped[str] = mapped_column(String(50), nullable=False)
    run_number: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("prompt_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    rendered_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    profile_variables: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    llm_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'pending'")
    )
    preprocessor_results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    postprocessor_results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    auto_evaluation: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    llm_judge_evaluation: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    session: Mapped["ManualSession"] = relationship(back_populates="step_runs")

    def __repr__(self) -> str:
        return f"<ManualStepRun(session={self.session_id}, step={self.step_name}, #{self.run_number})>"


from backend.src.models.manual_session import ManualSession  # noqa: E402
