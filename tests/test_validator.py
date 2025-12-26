from app.validation.basic import BasicValidator


def test_validate_json_pass():
    result = BasicValidator.validate(b'{"a": 1}', "JSON")
    assert result.status == "PASSED"


def test_validate_empty_fails():
    result = BasicValidator.validate(b"", "TEXT")
    assert result.status == "FAILED"
