from app.validation.detector import FormatDetector


def test_detect_json():
    payload = b'{"key": "value"}'
    result = FormatDetector.detect(payload)
    assert result["format"] == "JSON"


def test_detect_csv():
    payload = b"a,b\n1,2"
    result = FormatDetector.detect(payload)
    assert result["format"] == "CSV"
