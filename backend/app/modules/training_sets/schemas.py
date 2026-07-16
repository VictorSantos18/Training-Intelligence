from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TrainingSetResult(StrEnum):
    success = "SUCCESS"
    partial = "PARTIAL"
    failed = "FAILED"
    skipped = "SKIPPED"


class TechnicalQuality(StrEnum):
    excellent = "EXCELLENT"
    good = "GOOD"
    acceptable = "ACCEPTABLE"
    poor = "POOR"


class TrainingSetCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    set_number: int = Field(ge=1, le=999)
    repetitions: int | None = Field(default=None, ge=0, le=999)
    duration_seconds: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=2)
    assistance_level: Decimal | None = Field(default=None, max_digits=8, decimal_places=2)
    rpe: Decimal | None = Field(default=None, ge=0, le=10, max_digits=3, decimal_places=1)
    pain_during: int | None = Field(default=None, ge=0, le=10)
    result: TrainingSetResult
    technical_quality: TechnicalQuality | None = None
    rest_seconds: int | None = Field(default=None, ge=0, le=36000)
    notes: str | None = None

    @model_validator(mode="after")
    def require_metric_unless_skipped(self) -> "TrainingSetCreate":
        if (
            self.result != TrainingSetResult.skipped
            and self.repetitions is None
            and self.duration_seconds is None
        ):
            raise ValueError("Non-skipped sets require repetitions or duration_seconds")
        return self


class TrainingSetUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    set_number: int | None = Field(default=None, ge=1, le=999)
    repetitions: int | None = Field(default=None, ge=0, le=999)
    duration_seconds: Decimal | None = Field(default=None, ge=0, max_digits=6, decimal_places=2)
    assistance_level: Decimal | None = Field(default=None, max_digits=8, decimal_places=2)
    rpe: Decimal | None = Field(default=None, ge=0, le=10, max_digits=3, decimal_places=1)
    pain_during: int | None = Field(default=None, ge=0, le=10)
    result: TrainingSetResult | None = None
    technical_quality: TechnicalQuality | None = None
    rest_seconds: int | None = Field(default=None, ge=0, le=36000)
    notes: str | None = None

    @field_validator("set_number", "result", mode="before")
    @classmethod
    def disallow_null_for_required_if_present(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "TrainingSetUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class TrainingSetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_exercise_id: str
    set_number: int
    repetitions: int | None
    duration_seconds: Decimal | None
    assistance_level: Decimal | None
    rpe: Decimal | None
    pain_during: int | None
    result: TrainingSetResult
    technical_quality: TechnicalQuality | None
    rest_seconds: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

