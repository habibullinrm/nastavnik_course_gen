"""SQLAlchemy model for processor configurations."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.core.database import Base


class ProcessorConfig(Base):
    """Привязка пре/пост-процессоров к шагам в сессии."""

    __tablename__ = "processor_configs"

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
    )
    step_name: Mapped[str] = mapped_column(String(50), nullable=False)
    processor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    processor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    execution_order: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    config_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    session: Mapped["ManualSession"] = relationship(back_populates="processor_configs")

    def __repr__(self) -> str:
        return f"<ProcessorConfig({self.processor_type}:{self.processor_name} on {self.step_name})>"


from backend.src.models.manual_session import ManualSession  # noqa: E402
