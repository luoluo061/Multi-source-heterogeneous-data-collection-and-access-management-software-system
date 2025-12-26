from pathlib import Path
from typing import Optional


class SampleWriter:
    """Writes small payload samples for debugging."""

    def __init__(self, base_dir: Path = Path("data/samples")):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write(self, run_id: str, source_id: int, payload: bytes, suffix: str = "txt") -> Optional[Path]:
        try:
            path = self.base_dir / f"{run_id}_{source_id}.{suffix}"
            path.write_bytes(payload[:2000])
            return path
        except Exception:
            return None
