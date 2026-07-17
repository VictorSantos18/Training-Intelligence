from datetime import datetime

from pydantic import BaseModel

from app.modules.sessions.schemas import TrainingSessionStatus


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
