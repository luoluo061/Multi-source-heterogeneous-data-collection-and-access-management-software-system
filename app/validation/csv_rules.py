import csv
import io
from typing import Dict

from app.core.errors import ValidationError


class CsvRules:
    """Validates CSV structure with delimiter probing and row constraints."""

    DELIMS = [",", "\t", ";"]

    @staticmethod
    def probe_delimiter(text: str):
        best = ","
        max_cols = 0
        for delim in CsvRules.DELIMS:
            reader = csv.reader(io.StringIO(text), delimiter=delim)
            rows = list(reader)
            if rows and len(rows[0]) > max_cols:
                max_cols = len(rows[0])
                best = delim
        return best

    @staticmethod
    def validate(payload: bytes, *, max_rows: int = 10000) -> Dict:
        text = payload.decode("utf-8", errors="replace")
        delim = CsvRules.probe_delimiter(text)
        reader = csv.reader(io.StringIO(text), delimiter=delim)
        row_count = 0
        column_count = None
        for row in reader:
            row_count += 1
            if column_count is None:
                column_count = len(row)
            elif len(row) != column_count:
                raise ValidationError("CSV column count mismatch")
            if row_count > max_rows:
                raise ValidationError("CSV exceeds max rows")
        if row_count == 0:
            raise ValidationError("CSV has no rows")
        return {"delimiter": delim, "rows": row_count, "columns": column_count or 0}
