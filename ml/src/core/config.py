"""ML service configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ML service settings loaded from environment variables."""

    # DeepSeek API configuration
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_RETRIES: int = 3
    DEEPSEEK_RETRY_BACKOFF_BASE: int = 2

    # ML service configuration
    ML_HOST: str = "0.0.0.0"
    ML_PORT: int = 8001

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Global settings instance
settings = Settings()
