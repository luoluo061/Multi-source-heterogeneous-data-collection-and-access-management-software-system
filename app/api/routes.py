import json
from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.core.errors import SourceNotFoundError
from app.models.database import get_session
from app.models.entities import IngestionRun, RawRecord, SourceConfig
from app.schemas.health import RunHealth
from app.schemas.records import RecordReadSingle, RecordsResponse, RecordsPage
from app.schemas.events import RunEventsPage
from app.schemas.config import ConfigSnapshot
from app.schemas.record_stats import RecordStats
from app.schemas.history import RunHistoryResponse
from app.schemas.timeline import RunTimeline
from app.schemas.diagnostics import DiagnosticsSnapshot
from app.schemas.runs import RunListResponse, RunRead, TriggerResponse
from app.schemas.source_stats import SourceStats
from app.schemas.sources import SourceCreate, SourceRead, SourceUpdate
from app.schemas.summary import RunSummary
from app.services.ingestion_service import IngestionService
from app.services.run_filters import build_run_filters
from app.services.run_repository import RunRepository
from app.services.run_health import RunHealthService
from app.services.source_stats import SourceStatsService
from app.services.summary import RunSummaryService
from app.services.record_query import RecordQueryService
from app.services.events_service import EventsService
from app.services.config_service import ConfigService
from app.services.record_stats import RecordStatsService
from app.services.history_reader import HistoryReader
from app.services.run_timeline import RunTimelineService
from app.services.diagnostics import DiagnosticsService
from app.services.bulk_cancel import BulkCancelService
from app.services.source_manager import SourceManager

router = APIRouter()


@router.post("/sources", response_model=SourceRead)
def create_source(payload: SourceCreate, db: Session = Depends(get_session)):
    manager = SourceManager(db)
    return manager.create(payload)


@router.put("/sources/{source_id}", response_model=SourceRead)
def update_source(source_id: int, payload: SourceUpdate, db: Session = Depends(get_session)):
    manager = SourceManager(db)
    source = manager.update(source_id, payload)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.get("/sources", response_model=List[SourceRead])
def list_sources(db: Session = Depends(get_session)):
    return SourceManager(db).list()

@router.get("/sources/{source_id}/stats", response_model=SourceStats)
def source_stats(source_id: int, db: Session = Depends(get_session)):
    totals = SourceStatsService(db).stats_for_source(source_id)
    return SourceStats(totals=totals)


@router.post("/runs/trigger", response_model=TriggerResponse)
def trigger_run(source_id: int, db: Session = Depends(get_session)):
    service = IngestionService(db)
    try:
        run_id = service.trigger_run(source_id)
        return TriggerResponse(run_id=run_id, status="STARTED")
    except SourceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/runs/{run_id}", response_model=RunRead)
def get_run(run_id: str, db: Session = Depends(get_session)):
    run = db.query(IngestionRun).filter(IngestionRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/runs", response_model=RunListResponse)
def list_runs(
    source_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    from_ts: str | None = None,
    to_ts: str | None = None,
    db: Session = Depends(get_session),
):
    filters = build_run_filters(source_id, status, from_ts, to_ts)
    repo = RunRepository(db)
    runs = repo.list_runs(
        source_id=filters[0],
        status=filters[1],
        from_ts=filters[2],
        to_ts=filters[3],
        page=page,
        page_size=page_size,
    )
    return RunListResponse(items=runs)


@router.post("/runs/{run_id}/cancel")
def cancel_run(run_id: str, db: Session = Depends(get_session)):
    service = IngestionService(db)
    success = service.cancel_run(run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Run not found or already finished")
    return {"run_id": run_id, "status": "CANCELED_REQUESTED"}


@router.get("/runs/summary", response_model=RunSummary)
def run_summary(db: Session = Depends(get_session)):
    counts = RunSummaryService(db).counts()
    return RunSummary(counts=counts)


@router.get("/runs/health", response_model=RunHealth)
def run_health(db: Session = Depends(get_session)):
    counts = RunHealthService(db).snapshot()
    return RunHealth(counts=counts)


@router.get("/runs/{run_id}/events", response_model=RunEventsPage)
def list_run_events(run_id: str, page: int = 1, page_size: int = 50, db: Session = Depends(get_session)):
    total, items = EventsService(db).list(run_id, page=page, page_size=page_size)
    return RunEventsPage(page=page, page_size=page_size, total=total, items=items)


@router.get("/config", response_model=ConfigSnapshot)
def get_config():
    return ConfigService().snapshot()


@router.get("/records/stats", response_model=RecordStats)
def records_stats(db: Session = Depends(get_session)):
    svc = RecordStatsService(db)
    return RecordStats(totals=svc.totals(), by_format=svc.by_format(), by_status=svc.by_status())


@router.get("/runs/{run_id}/history", response_model=RunHistoryResponse)
def run_history(run_id: str):
    lines = HistoryReader().read(run_id)
    return RunHistoryResponse(run_id=run_id, lines=[{"raw": line} for line in lines])


@router.get("/runs/{run_id}/timeline", response_model=RunTimeline)
def run_timeline(run_id: str, db: Session = Depends(get_session)):
    run = db.query(IngestionRun).filter(IngestionRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    events = EventsService(db).list(run_id, page=1, page_size=500)[1]
    timeline = RunTimelineService(run, events).build()
    return RunTimeline(run_id=run_id, items=timeline)


@router.get("/diagnostics", response_model=DiagnosticsSnapshot)
def diagnostics(db: Session = Depends(get_session)):
    return DiagnosticsSnapshot(**DiagnosticsService(db).snapshot())


@router.post("/runs/cancel")
def cancel_pending(source_id: int, db: Session = Depends(get_session)):
    ids = BulkCancelService(db).cancel_pending(source_id)
    return {"source_id": source_id, "canceled": ids}


@router.get("/records", response_model=RecordsPage)
def list_records(
    run_id: str | None = None,
    source_id: int | None = None,
    format: str | None = None,
    validation_status: str | None = None,
    from_time: str | None = None,
    to_time: str | None = None,
    sort: str = "desc",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_session),
):
    service = RecordQueryService(db)
    total, items = service.list_records(
        run_id=run_id,
        source_id=source_id,
        fmt=format,
        validation_status=validation_status,
        from_time=from_time,
        to_time=to_time,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return RecordsPage(page=page, page_size=page_size, total=total, items=items)


@router.get("/records/{record_id}", response_model=RecordReadSingle)
def get_record(record_id: int, db: Session = Depends(get_session)):
    service = RecordQueryService(db)
    record = service.get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.get("/records/{record_id}/payload")
def get_record_payload(record_id: int, db: Session = Depends(get_session)):
    service = RecordQueryService(db)
    payload, content_type = service.get_payload(record_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"record_id": record_id, "content_type": content_type, "payload": payload.decode("utf-8", errors="replace")}


def create_app() -> FastAPI:
    app = FastAPI(title="Multi-source data ingestion")
    app.include_router(router)
    return app
