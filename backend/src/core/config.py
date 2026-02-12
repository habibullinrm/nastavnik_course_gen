"""Backend configuration using Pydantic Settings."""

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

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Global settings instance
settings = Settings()
