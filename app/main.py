from fastapi import FastAPI

from app.api.routes import create_app
from app.core.config import settings
from app.core.logging import configure_logging
from app.models import entities  # noqa: F401 - ensure model registration
from app.models.database import Base, SessionLocal, engine
from app.scheduler.scheduler import Scheduler


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def build_app() -> FastAPI:
    configure_logging()
    init_db()
    app = create_app()
    scheduler = Scheduler(SessionLocal, interval_seconds=settings.scheduler_interval_seconds)

    @app.on_event("startup")
    async def _start_scheduler():
        scheduler.start()

    @app.on_event("shutdown")
    async def _stop_scheduler():
        scheduler.stop()

    return app


app = build_app()
