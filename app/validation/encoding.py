import codecs
from typing import List


class EncodingDetector:
    """Basic encoding detector with UTF-8/GBK/Latin-1 fallbacks."""

    FALLBACKS: List[str] = ["utf-8", "gbk", "latin-1"]

    @staticmethod
    def detect(data: bytes) -> str:
        for enc in EncodingDetector.FALLBACKS:
            try:
                data.decode(enc)
                return enc
            except Exception:
                continue
        return "utf-8"
