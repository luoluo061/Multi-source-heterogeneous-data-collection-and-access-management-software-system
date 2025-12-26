from typing import Dict


class HttpAuth:
    """Builds authentication headers."""

    @staticmethod
    def bearer(token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"} if token else {}
