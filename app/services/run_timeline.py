from typing import List

from app.models.entities import IngestionRun, RunEvent
from app.schemas.timeline import TimelineEntry
from app.services.run_event_formatter import RunEventFormatter


class RunTimelineService:
    """Builds a timeline from run and event data."""

    def __init__(self, run: IngestionRun, events: List[RunEvent]):
        self.run = run
        self.events = events

    def build(self) -> List[TimelineEntry]:
        items: List[TimelineEntry] = []
        if self.run.started_at:
            items.append(
                TimelineEntry(
                    label="Run started",
                    ts=self.run.started_at.isoformat(),
                    message=self.run.message or "",
                    stage="RUN",
                )
            )
        for ev in self.events:
            formatted = RunEventFormatter.to_dict(ev)
            items.append(
                TimelineEntry(
                    label=formatted["event_type"],
                    ts=formatted["ts"],
                    message=formatted["message"],
                    stage=formatted["stage"],
                )
            )
        if self.run.finished_at:
            items.append(
                TimelineEntry(
                    label=f"Run {self.run.status}",
                    ts=self.run.finished_at.isoformat(),
                    message=self.run.message or "",
                    stage="RUN",
                )
            )
        return items
