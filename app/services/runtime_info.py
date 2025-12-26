import platform
import sys
from typing import Dict

from app.core.logging import get_logger


class RuntimeInfo:
    """Reports runtime environment details for diagnostics."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def emit(self):
        payload: Dict[str, str] = {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": str(platform.machine()),
            "executable": sys.executable,
            "machine": platform.node(),
            "timezone": str(datetime.now().astimezone().tzinfo),
            "cwd": str(Path.cwd()),
            "env_vars": str(len(os.environ)),
            "python_build": str(platform.python_build()),
            "python_impl": platform.python_implementation(),
            "platform_release": platform.release(),
            "system": platform.system(),
            "platform_version": platform.version(),
        }
        self.logger.info("runtime_info", extra={"run_id": "-", "source_id": "-", "payload": payload})
        return payload

    def as_dict(self) -> Dict[str, str]:
        return self.emit()
