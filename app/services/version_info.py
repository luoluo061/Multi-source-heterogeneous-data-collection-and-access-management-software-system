import platform


class VersionInfo:
    """Collects version strings."""

    @staticmethod
    def snapshot() -> dict:
        return {"python": platform.python_version(), "platform": platform.platform()}
