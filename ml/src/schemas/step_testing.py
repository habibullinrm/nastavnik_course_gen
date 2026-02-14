"""
Схемы для тестирования отдельных шагов B1-B8.

Позволяют запускать каждый шаг изолированно через API endpoints
с возможностью использования mock или real LLM client.
"""

from pydantic import BaseModel, Field


class StepTestRequest(BaseModel):
    """
    Запрос для тестирования отдельного шага пайплайна.

    Attributes:
        use_mock: Использовать MockLLMClient (True) или DeepSeekClient (False)
        inputs: Входные данные для шага (структура зависит от конкретного шага)
        step_name: Явное указание шага (B1_validate, B2_competencies, etc.) - используется для mock LLM
    """

    use_mock: bool = Field(
        default=True,
        description="Использовать mock LLM (True) или реальный DeepSeek (False)",
    )
    inputs: dict = Field(
        ...,
        description="Входные данные для шага (structure depends on step)",
    )
    step_name: str | None = Field(
        default=None,
        description="Явное указание шага для mock LLM (e.g., 'B1_validate', 'B2_competencies')",
    )


class StepTestResponse(BaseModel):
    """
    Ответ при тестировании отдельного шага пайплайна.

    Attributes:
        step_name: Название шага (B1, B2, ..., B8)
        success: Успешность выполнения шага
        output: Результат шага (OutputSchema в виде dict)
        metadata: Метаданные LLM (tokens, duration, model)
        error: Описание ошибки (если success=False)
    """

    step_name: str = Field(..., description="Название шага (B1-B8)")
    success: bool = Field(..., description="Успешность выполнения")
    output: dict = Field(
        default_factory=dict,
        description="Результат шага (OutputSchema as dict)",
    )
    metadata: dict = Field(
        default_factory=dict,
        description="LLM metadata (tokens, duration, model)",
    )
    error: str | None = Field(
        default=None,
        description="Описание ошибки при неуспешном выполнении",
    )
