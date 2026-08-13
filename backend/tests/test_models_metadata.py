import app.models  # noqa: F401
from app.db.base import Base


def test_initial_domain_tables_are_registered() -> None:
    assert {
        "profiles",
        "skills",
        "exercises",
        "training_sessions",
        "session_exercises",
        "training_sets",
        "body_regions",
        "pain_records",
        "training_analysis_reports",
        "training_analysis_report_sessions",
    }.issubset(Base.metadata.tables.keys())


def test_initial_domain_tables_keep_user_ownership() -> None:
    skills = Base.metadata.tables["skills"]
    exercises = Base.metadata.tables["exercises"]
    pain_records = Base.metadata.tables["pain_records"]
    training_analysis_reports = Base.metadata.tables["training_analysis_reports"]

    assert "user_id" in skills.c
    assert "user_id" in exercises.c
    assert "user_id" in pain_records.c
    assert "user_id" in training_analysis_reports.c
