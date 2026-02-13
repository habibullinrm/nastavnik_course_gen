"""
Health check endpoint для Backend сервиса.

Проверяет:
- Статус самого сервиса
- Доступность PostgreSQL БД
- Доступность ML сервиса
"""

import httpx
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.config import settings
from backend.src.core.database import get_db

router = APIRouter(prefix="/api/health", tags=["health"])


class HealthResponse(BaseModel):
    """Ответ health check."""

    status: str
    service: str
    database_available: bool
    ml_service_available: bool


@router.get("/", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Проверка здоровья Backend сервиса.

    Проверяет:
    - Подключение к PostgreSQL через SELECT 1
    - Доступность ML сервиса через GET /health

    Args:
        db: Сессия базы данных

    Returns:
        HealthResponse: Статус сервиса и зависимостей
    """
    # Проверка БД
    database_available = False
    try:
        result = await db.execute(text("SELECT 1"))
        database_available = result.scalar() == 1
    except Exception:
        database_available = False

    # Проверка ML сервиса
    ml_service_available = False
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            response = await client.get(f"{settings.ML_SERVICE_URL}/health")
            ml_service_available = response.status_code == 200
    except Exception:
        ml_service_available = False

    return HealthResponse(
        status="healthy" if (database_available and ml_service_available) else "degraded",
        service="backend",
        database_available=database_available,
        ml_service_available=ml_service_available,
    )
