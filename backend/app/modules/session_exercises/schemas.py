from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SessionExerciseCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    exercise_id: UUID
    execution_order: int = Field(ge=1, le=999)
    notes: str | None = None


class SessionExerciseUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    execution_order: int | None = Field(default=None, ge=1, le=999)
    notes: str | None = None

    @field_validator("execution_order", mode="before")
    @classmethod
    def disallow_null_execution_order(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "SessionExerciseUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class SessionExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    exercise_id: str
    execution_order: int
    notes: str | None
    created_at: datetime

