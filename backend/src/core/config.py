"""Backend configuration using Pydantic Settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    POSTGRES_USER: str = "nastavnik"
    POSTGRES_PASSWORD: str = "nastavnik_dev"
    POSTGRES_DB: str = "nastavnik_testing"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    # Backend configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # ML Service configuration
    ML_SERVICE_URL: str = "http://ml:8001"

    # CORS: comma-separated list of allowed origins
    # Dev default: localhost + Docker frontend container
    CORS_ORIGINS: str = "http://localhost:3000,http://frontend:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors_origins(cls, v: str) -> str:
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Global settings instance
settings = Settings()
