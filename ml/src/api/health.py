"""
Health check endpoint для ML сервиса.

Проверяет:
- Статус самого сервиса
- Доступность DeepSeek API
"""

from fastapi import APIRouter, status
from pydantic import BaseModel

from ml.src.services.deepseek_client import get_deepseek_client

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Ответ health check."""

    status: str
    service: str
    deepseek_available: bool


@router.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Проверка здоровья ML сервиса.

    Проверяет доступность DeepSeek API через ping-запрос.

    Returns:
        HealthResponse: Статус сервиса и доступность DeepSeek
    """
    deepseek_available = False

    try:
        # Проверка доступности DeepSeek API
        client = get_deepseek_client()
        # Простой проверочный запрос (минимальный токен usage)
        response = await client.post(
            "/chat/completions",
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1,
            },
            timeout=5.0,
        )
        deepseek_available = response.status_code == 200
    except Exception:
        # Любая ошибка = API недоступен
        deepseek_available = False

    return HealthResponse(
        status="healthy",
        service="ml",
        deepseek_available=deepseek_available,
    )
