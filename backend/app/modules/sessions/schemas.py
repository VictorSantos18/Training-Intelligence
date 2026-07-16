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
    body_weight_kg: Decimal | None = Field(default=None, ge=0, max_digits=5, decimal_places=2)
    sleep_hours: Decimal | None = Field(default=None, ge=0, le=24, max_digits=4, decimal_places=2)
    sleep_quality: int | None = Field(default=None, ge=0, le=10)
    energy_before: int | None = Field(default=None, ge=0, le=10)
    motivation_before: int | None = Field(default=None, ge=0, le=10)
    fatigue_before: int | None = Field(default=None, ge=0, le=10)
    notes_before: str | None = None


class TrainingSessionUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    skill_id: UUID | None = None
    started_at: datetime | None = None
    body_weight_kg: Decimal | None = Field(default=None, ge=0, max_digits=5, decimal_places=2)
    sleep_hours: Decimal | None = Field(default=None, ge=0, le=24, max_digits=4, decimal_places=2)
    sleep_quality: int | None = Field(default=None, ge=0, le=10)
    energy_before: int | None = Field(default=None, ge=0, le=10)
    motivation_before: int | None = Field(default=None, ge=0, le=10)
    fatigue_before: int | None = Field(default=None, ge=0, le=10)
    notes_before: str | None = None

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
    fatigue_after: int | None = Field(default=None, ge=0, le=10)
    performance_rating: int | None = Field(default=None, ge=0, le=10)
    notes_after: str | None = None


class TrainingSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_id: str | None
    started_at: datetime
    finished_at: datetime | None
    body_weight_kg: Decimal | None
    sleep_hours: Decimal | None
    sleep_quality: int | None
    energy_before: int | None
    motivation_before: int | None
    fatigue_before: int | None
    fatigue_after: int | None
    performance_rating: int | None
    notes_before: str | None
    notes_after: str | None
    status: TrainingSessionStatus
    created_at: datetime
    updated_at: datetime
