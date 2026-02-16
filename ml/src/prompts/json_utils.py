"""JSON utilities for prompt serialization."""

import json
from typing import Any


class PydanticEncoder(json.JSONEncoder):
    """JSON encoder that handles Pydantic models and other common types."""

    def default(self, obj: Any) -> Any:
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return super().default(obj)


def to_json(data: Any) -> str:
    """Serialize data to JSON string, handling Pydantic models."""
    return json.dumps(data, cls=PydanticEncoder, ensure_ascii=False, indent=2)