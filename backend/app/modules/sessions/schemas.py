from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TrainingSessionStatus(StrEnum):
    in_progress = "IN_PROGRESS"
    completed = "COMPLETED"
    cancelled = "CANCELLED"


class TrainingSessionCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    skill_id: UUID | None = None
    started_at: datetime
    sleep_hours: Decimal | None = Field(default=None, ge=0, le=24, max_digits=4, decimal_places=2)
    energy_before: int | None = Field(default=None, ge=0, le=10)


class TrainingSessionUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    skill_id: UUID | None = None
    started_at: datetime | None = None
    sleep_hours: Decimal | None = Field(default=None, ge=0, le=24, max_digits=4, decimal_places=2)
    energy_before: int | None = Field(default=None, ge=0, le=10)

    @field_validator("started_at", mode="before")
    @classmethod
    def disallow_null_started_at(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "TrainingSessionUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class TrainingSessionFinish(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    finished_at: datetime | None = None
    notes_after: str | None = None


class TrainingSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_id: str | None
    started_at: datetime
    finished_at: datetime | None
    sleep_hours: Decimal | None
    energy_before: int | None
    notes_after: str | None
    status: TrainingSessionStatus
    created_at: datetime
    updated_at: datetime
