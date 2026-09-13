"""Validated commands shared by every interaction adapter and the core."""
from pydantic import BaseModel, ConfigDict, Field


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tool: str = Field(min_length=1, max_length=100)
    arguments: dict = Field(default_factory=dict)


class TaskRequest(ToolCall):
    objective: str = Field(min_length=1, max_length=2000)
    profile: str | None = Field(default=None, max_length=100)
    delay_seconds: float = Field(default=0, ge=0, le=30, allow_inf_nan=False)
