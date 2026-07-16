import app.models  # noqa: F401
from app.db.base import Base


def test_initial_domain_tables_are_registered() -> None:
    assert {"profiles", "skills", "exercises", "training_sessions"}.issubset(
        Base.metadata.tables.keys()
    )


def test_initial_domain_tables_keep_user_ownership() -> None:
    skills = Base.metadata.tables["skills"]
    exercises = Base.metadata.tables["exercises"]

    assert "user_id" in skills.c
    assert "user_id" in exercises.c
