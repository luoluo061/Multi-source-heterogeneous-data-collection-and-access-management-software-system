class RecordLimiter:
    """Applies bounds to page sizes for record queries."""

    def __init__(self, max_page_size: int = 500):
        self.max_page_size = max_page_size

    def clamp(self, page_size: int) -> int:
        if page_size <= 0:
            return 1
        return min(page_size, self.max_page_size)
