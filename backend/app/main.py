from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.me import router as me_router
from app.core.config import settings
from app.modules.exercises.router import router as exercises_router
from app.modules.session_exercises.router import router as session_exercises_router
from app.modules.sessions.router import router as sessions_router
from app.modules.skills.router import router as skills_router
from app.modules.training_sets.router import router as training_sets_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Training Intelligence API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(me_router)
    app.include_router(skills_router)
    app.include_router(exercises_router)
    app.include_router(sessions_router)
    app.include_router(session_exercises_router)
    app.include_router(training_sets_router)
    return app


app = create_app()
