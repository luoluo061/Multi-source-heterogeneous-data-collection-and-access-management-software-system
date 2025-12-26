import hashlib
import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from app.adapters.factory import get_adapter
from app.core.error_codes import ErrorCode
from app.core.errors import AdapterError, IngestionError, RetryableError, SourceNotFoundError, StorageError, ValidationError
from app.core.logging import get_logger
from app.models.entities import IngestionRun, RawRecord, SourceConfig
from app.services.metrics import RunMetrics
from app.services.statistics import RunStatistics
from app.services.run_manager import RunManager
from app.services.run_reporter import RunReporter
from app.services.run_state import RunStatus
from app.services.run_context import new_context
from app.services.debug_tools import DebugTools
from app.services.log_enricher import LogEnricher
from app.services.run_flags import RunFlags
from app.services.run_tags import RunTags
from app.services.runtime_info import RuntimeInfo
from app.services.source_validator import SourceValidator
from app.services.event_logger import EventLogger
from app.services.event_constants import EventType
from app.services.payload_audit import PayloadAudit
from app.services.run_labeler import RunLabeler
from app.services.run_metrics_logger import RunMetricsLogger
from app.services.trace_context import TraceContext, TraceEmitter
from app.services.payload_stats import PayloadStats
from app.storage.payload_service import PayloadService
from app.storage.record_builder import RecordBuilder
from app.storage.sample_writer import SampleWriter
from app.validation.basic import BasicValidator
from app.validation.detector import FormatDetector
from app.validation.payload import PayloadValidator


class IngestionService:
    """Coordinates end-to-end ingestion for a single source."""

    def __init__(self, db: Session):
        self.db = db
        self.run_manager = RunManager(db)
        self.reporter = RunReporter()
        self.sample_writer = SampleWriter()
        self.debug_tools = DebugTools()
        self.log_enricher = LogEnricher()
        self.run_tags = RunTags()
        self.runtime_info = RuntimeInfo()
        self.event_logger = EventLogger(db)
        self.payload_audit = PayloadAudit()
        self.run_labeler = RunLabeler()
        self.metrics_logger = RunMetricsLogger()
        self.trace_emitter = TraceEmitter()
        self.payload_stats = PayloadStats()

    def trigger_run(self, source_id: int) -> str:
        run = self.run_manager.create_run(source_id)
        source = self.db.query(SourceConfig).filter(SourceConfig.id == source_id).first()
        if run.status == RunStatus.PENDING.value:
            # start immediately if no other active run
            SourceValidator.validate(source.type, source.params_dict())
            self.debug_tools.snapshot_source(source)
            runtime_snapshot = self.runtime_info.as_dict()
            self.log_enricher.emit(run.run_id, source.id, {"runtime": runtime_snapshot})
            context = new_context(run.run_id, source.id, schedule_triggered=False, metadata={"type": source.type})
            self.debug_tools.dump_run_context(run.run_id, context.as_dict())
            self.log_enricher.emit(run.run_id, source.id, {"phase": "init", "source": source.name})
            flags = RunFlags(manual_trigger=True, scheduled=False).to_payload()
            self.run_tags.attach(run.run_id, source.id, tags=["ingestion"], attributes={"source_type": source.type, **flags})
            self.event_logger.log(run.run_id, stage="RUN", event_type=EventType.RUN_STARTED, message="Run created")
            self.trace_emitter.emit(TraceContext(run.run_id, source.id, correlation_id=run.run_id))
            self._execute_run(run, source)
        return run.run_id

    def cancel_run(self, run_id: str) -> bool:
        return self.run_manager.request_cancel(run_id)

    def _execute_run(self, run: IngestionRun, source: SourceConfig) -> None:
        logger = get_logger(__name__, run_id=run.run_id, source_id=str(source.id))
        metrics = RunMetrics(started_at=datetime.now(timezone.utc))
        stats = RunStatistics()
        self.run_manager.start_run(run)
        self.reporter.started(run.run_id, source.id)
        adapter = get_adapter(source.type, source.params_dict())
        try:
            def _run_fetch():
                self.event_logger.log(run.run_id, stage="FETCH", event_type=EventType.FETCH_STARTED, message="Starting fetch")
                payloads = adapter.fetch()
                self.event_logger.log(run.run_id, stage="FETCH", event_type=EventType.FETCH_DONE, message=f"Fetched {len(payloads)} payloads")
                stored_items = self._process_payloads(payloads, run, source.id, metrics, stats)
                run.message = f"Stored {len(stored_items)} records"
                logger.info(run.message)

            self.run_manager.execute_with_retry(_run_fetch, metrics, run)
            metrics.finished_at = datetime.now(timezone.utc)
            self.run_manager.finalize_run(run, metrics, RunStatus.SUCCESS, error_code=ErrorCode.UNKNOWN)
            self.reporter.finished(
                run.run_id,
                source.id,
                RunStatus.SUCCESS,
                {"records": stats.records, "bytes": stats.bytes_total, "duration_ms": metrics.duration_ms},
            )
            self.log_enricher.complete(run.run_id, source.id, {"status": "SUCCESS", "records": stats.records})
            self.event_logger.log(run.run_id, stage="RUN", event_type=EventType.RUN_SUCCESS, message="Run succeeded")
            self.metrics_logger.log(run.run_id, source.id, metrics)
        except (AdapterError, RetryableError, StorageError, ValidationError) as exc:
            metrics.finished_at = datetime.now(timezone.utc)
            self.run_manager.finalize_run(run, metrics, RunStatus.FAILED, error_code=getattr(exc, "error_code", ErrorCode.UNKNOWN), error_message=str(exc))
            logger.exception("Run failed")
            self.log_enricher.failure(run.run_id, source.id, str(exc))
            self.event_logger.log(run.run_id, stage="RUN", event_type=EventType.RUN_FAILED, message=str(exc), error_code=getattr(exc, "error_code", None))
        except SourceNotFoundError as exc:
            metrics.finished_at = datetime.now(timezone.utc)
            self.run_manager.finalize_run(run, metrics, RunStatus.FAILED, error_code=ErrorCode.SOURCE_NOT_FOUND, error_message=str(exc))
            logger.exception("Run failed")
            self.log_enricher.failure(run.run_id, source.id, str(exc))
            self.event_logger.log(run.run_id, stage="RUN", event_type=EventType.RUN_FAILED, message=str(exc), error_code=ErrorCode.SOURCE_NOT_FOUND)
        except IngestionError as exc:
            metrics.finished_at = datetime.now(timezone.utc)
            self.run_manager.finalize_run(run, metrics, RunStatus.FAILED, error_code=getattr(exc, "error_code", ErrorCode.UNKNOWN), error_message=str(exc))
            logger.exception("Run failed")
            self.log_enricher.failure(run.run_id, source.id, str(exc))
            self.event_logger.log(run.run_id, stage="RUN", event_type=EventType.RUN_FAILED, message=str(exc), error_code=getattr(exc, "error_code", None))
        finally:
            if self.run_manager.should_cancel(run):
                self.reporter.canceled(run.run_id, source.id)
                self.run_tags.annotate(run.run_id, source.id, "canceled_by_request")
                self.event_logger.log(run.run_id, stage="RUN", event_type=EventType.RUN_CANCELED, message="Cancellation requested")

    def _process_payloads(self, payloads: List[dict], run: IngestionRun, source_id: int, metrics: RunMetrics, stats: RunStatistics) -> List[RawRecord]:
        builder = RecordBuilder(run.run_id, source_id)
        records = builder.build_many(payloads, FormatDetector, BasicValidator)
        self.event_logger.log(run.run_id, stage="PROCESS", event_type=EventType.DETECT_DONE, message=f"Detected {len(records)} payloads")
        for rec in records:
            payload_bytes = rec["payload"]
            metrics.add_payload(payload_bytes)
            stats.update(payload_bytes)
        self.event_logger.log(run.run_id, stage="VALIDATION", event_type=EventType.VALIDATION_DONE, message="Validation completed")
        self.payload_audit.log(run.run_id, source_id, records)
        stats_summary = self.payload_stats.summarize(records)
        self.log_enricher.emit(run.run_id, source_id, {"payload_stats": stats_summary})
        labels = self.run_labeler.labels_for_payloads(records)
        self.run_tags.annotate(run.run_id, source_id, f"formats:{labels}")
        stored = PayloadService(self.db).persist(run_id=run.run_id, source_id=source_id, records=records)
        run.records_count = stats.records
        run.bytes_total = stats.bytes_total
        self.event_logger.log(run.run_id, stage="STORAGE", event_type=EventType.STORAGE_DONE, message=f"Persisted {len(stored)} records")
        if records:
            sample = records[0]["payload"]
            self.sample_writer.write(run.run_id, source_id, sample)
        return stored
