from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ExerciseCategory(StrEnum):
    hold = "HOLD"
    press = "PRESS"
    pull = "PULL"
    raise_ = "RAISE"
    negative = "NEGATIVE"
    accessory = "ACCESSORY"


class ExerciseMeasurementType(StrEnum):
    reps = "REPS"
    seconds = "SECONDS"
    distance = "DISTANCE"
    custom = "CUSTOM"


class ExerciseCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    skill_id: UUID | None = None
    name: str = Field(min_length=1, max_length=150)
    category: ExerciseCategory
    measurement_type: ExerciseMeasurementType


class ExerciseUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    skill_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=150)
    category: ExerciseCategory | None = None
    measurement_type: ExerciseMeasurementType | None = None
    is_active: bool | None = None

    @field_validator("name", "category", "measurement_type", "is_active", mode="before")
    @classmethod
    def disallow_null_for_non_nullable_fields(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "ExerciseUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class ExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_id: str | None
    name: str
    category: ExerciseCategory
    measurement_type: ExerciseMeasurementType
    is_active: bool
    created_at: datetime
    updated_at: datetime

