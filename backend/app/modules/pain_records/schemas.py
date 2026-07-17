from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PainRecordMoment(StrEnum):
    pre_session = "PRE_SESSION"
    during_set = "DURING_SET"
    post_session = "POST_SESSION"
    checkin_24h = "CHECKIN_24H"
    checkin_48h = "CHECKIN_48H"


class PainRecordSide(StrEnum):
    left = "LEFT"
    right = "RIGHT"
    bilateral = "BILATERAL"
    not_applicable = "NOT_APPLICABLE"


class PainRecordCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    training_session_id: UUID | None = None
    training_set_id: UUID | None = None
    body_region_id: UUID
    occurred_at: datetime | None = None
    side: PainRecordSide
    moment: PainRecordMoment
    intensity: int = Field(ge=0, le=10)
    description: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def require_training_context(self) -> "PainRecordCreate":
        if self.training_session_id is None and self.training_set_id is None:
            raise ValueError("Pain records require training_session_id or training_set_id")
        if self.moment == PainRecordMoment.during_set and self.training_set_id is None:
            raise ValueError("DURING_SET pain records require training_set_id")
        return self


class PainRecordUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    occurred_at: datetime | None = None
    body_region_id: UUID | None = None
    side: PainRecordSide | None = None
    moment: PainRecordMoment | None = None
    intensity: int | None = Field(default=None, ge=0, le=10)
    description: str | None = None
    notes: str | None = None

    @field_validator("body_region_id", "side", "moment", "intensity", mode="before")
    @classmethod
    def disallow_null_for_required_if_present(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "PainRecordUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class PainRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    training_session_id: str | None
    training_set_id: str | None
    body_region_id: str
    occurred_at: datetime
    side: PainRecordSide
    moment: PainRecordMoment
    intensity: int
    description: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
