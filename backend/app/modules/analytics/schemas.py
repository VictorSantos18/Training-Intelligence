from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.sessions.schemas import TrainingSessionStatus


class AnalysisReportStatus(StrEnum):
    prompt_generated = "PROMPT_GENERATED"
    analysis_saved = "ANALYSIS_SAVED"


class AnalyticsStats(BaseModel):
    total_sessions: int
    completed_sessions: int
    in_progress_sessions: int
    cancelled_sessions: int
    total_sets: int
    pain_records: int
    average_energy_before: float | None
    average_sleep_hours: float | None


class SessionsBySkillItem(BaseModel):
    skill_id: str | None
    skill_name: str
    session_count: int
    completed_count: int


class RecentSessionItem(BaseModel):
    id: str
    skill_name: str
    status: TrainingSessionStatus
    started_at: datetime
    finished_at: datetime | None


class TopExerciseItem(BaseModel):
    exercise_id: str
    exercise_name: str
    set_count: int
    success_count: int
    total_repetitions: int
    total_duration_seconds: float


class PainByRegionItem(BaseModel):
    body_region_id: str
    body_region_name: str
    record_count: int
    average_intensity: float
    max_intensity: int


class AnalyticsOverview(BaseModel):
    stats: AnalyticsStats
    sessions_by_skill: list[SessionsBySkillItem]
    recent_sessions: list[RecentSessionItem]
    top_exercises: list[TopExerciseItem]
    pain_by_region: list[PainByRegionItem]


class AnalysisReportGenerate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    period_start: date
    period_end: date
    skill_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=160)

    @model_validator(mode="after")
    def validate_period(self) -> "AnalysisReportGenerate":
        if self.period_end < self.period_start:
            raise ValueError("period_end must be greater than or equal to period_start")
        return self


class AnalysisReportUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=160)
    external_analysis: str | None = None

    @field_validator("title", mode="before")
    @classmethod
    def disallow_null_title(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Field cannot be null")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "AnalysisReportUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class AnalysisReportSessionLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_report_id: str
    training_session_id: str
    created_at: datetime


class AnalysisReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_id: str | None
    title: str
    period_start: date
    period_end: date
    filters: dict[str, Any]
    summary_snapshot: dict[str, Any]
    generated_prompt: str
    external_analysis: str | None
    status: AnalysisReportStatus
    created_at: datetime
    updated_at: datetime
    sessions: list[AnalysisReportSessionLinkRead] = []


class AnalysisReportListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    skill_id: str | None
    title: str
    period_start: date
    period_end: date
    status: AnalysisReportStatus
    created_at: datetime
    updated_at: datetime
