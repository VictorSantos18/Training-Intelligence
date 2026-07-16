from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SkillStatus(StrEnum):
    active = "ACTIVE"
    paused = "PAUSED"
    achieved = "ACHIEVED"


class SkillCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    status: SkillStatus = SkillStatus.active


class SkillUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    status: SkillStatus | None = None

    @field_validator("name", "status", mode="before")
    @classmethod
    def disallow_null_for_required_fields(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "SkillUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class SkillRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None
    status: SkillStatus
    created_at: datetime
    updated_at: datetime
