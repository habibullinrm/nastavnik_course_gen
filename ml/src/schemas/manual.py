"""Pydantic schemas for manual mode ML endpoints."""

from typing import Any

from pydantic import BaseModel, Field


class ManualExecuteRequest(BaseModel):
    """Request to execute a step with custom prompt."""
    step_name: str
    prompt: str
    input_data: dict[str, Any] | None = None
    llm_params: dict[str, Any] | None = None
    use_mock: bool = True


class ManualExecuteResponse(BaseModel):
    """Response from step execution."""
    raw_response: str | None
    parsed_result: dict[str, Any] | None
    tokens_used: int
    duration_ms: float
    model: str
    parse_error: str | None


class RenderPromptRequest(BaseModel):
    """Request to render a prompt template."""
    step_name: str
    profile: dict[str, Any]
    extra_data: dict[str, Any] | None = None


class RenderPromptResponse(BaseModel):
    """Response with rendered prompt."""
    step_name: str
    rendered_prompt: str
    variables_used: list[str]


class BaselinePrompt(BaseModel):
    """Baseline prompt info."""
    step_name: str
    prompt_text: str
    function_name: str


class BaselinePromptsResponse(BaseModel):
    """Response with all baseline prompts."""
    prompts: list[BaselinePrompt]


class ProcessorMeta(BaseModel):
    """Processor metadata from PROCESSOR_META."""
    name: str
    type: str
    applicable_steps: list[str]
    description: str


class ProcessorsListResponse(BaseModel):
    """Response with available processors."""
    processors: list[ProcessorMeta]


class ProcessorRunRequest(BaseModel):
    """Request to run a processor."""
    processor_name: str
    data: dict[str, Any]
    step_name: str
    config_params: dict[str, Any] | None = None


class ProcessorRunResponse(BaseModel):
    """Response from processor run."""
    name: str
    passed: bool
    output: dict[str, Any] | None = None
    message: str | None = None
    error: str | None = None


class EvaluateRequest(BaseModel):
    """Request for evaluation (auto-metrics + optional LLM judge)."""
    step_name: str
    parsed_result: dict[str, Any]
    input_data: dict[str, Any] | None = None
    run_llm_judge: bool = False
    use_mock: bool = True


class EvaluateResponse(BaseModel):
    """Evaluation results."""
    auto_evaluation: dict[str, Any]
    llm_judge_evaluation: dict[str, Any] | None = None
