import pytest
from metacogitor.exceptions import ErrorDetails
from pydantic import ValidationError
import json

# TODO: enable this test after removing default values from ErrorDetails
"""
def test_error_details_required_fields():
    # Should raise ValueError if required fields not passed
    with pytest.raises(ValueError):
        ErrorDetails()

    with pytest.raises(ValueError):
        ErrorDetails(message="Missing code")

    with pytest.raises(ValueError):
        ErrorDetails(code=123)
"""


def test_error_details_extra_fields():
    # Should allow extra fields like transaction_id
    details = ErrorDetails(message="Test error", code=123, transaction_id="TX123")
    assert details.dict() == {
        "message": "Test error",
        "code": 123,
        "transaction_id": "TX123",
    }


@pytest.mark.parametrize("code,message", [(123, "First error"), (456, "Second error")])
def test_error_details_instances(code, message):
    details = ErrorDetails(code=code, message=message)
    assert details.code == code
    assert details.message == message


def test_length():
    # Check message length
    details = ErrorDetails(code=123, message="x" * 300)
    assert len(details.message) == 300

    with pytest.raises(ValidationError):
        ErrorDetails(code=1230, message="x" * 256)

    with pytest.raises(ValidationError):
        ErrorDetails(code=-1230, message="x" * 256)


def test_code_type():
    # Check code is integer
    with pytest.raises(ValidationError):
        ErrorDetails(message="Error", code="abc")


def test_serialization():
    details = ErrorDetails(code=123, message="Error", transaction_id="TX123")

    json_data = details.json()
    test_data = json.dumps({"message": "Error", "code": 123, "transaction_id": "TX123"})
    assert json_data == test_data

    data = json.loads(json_data)
    loaded = ErrorDetails(**data)
    assert loaded == details


@pytest.mark.parametrize(
    "code,message", [(123, "Error 1"), (456, "Error 2"), (789, "Error 3")]
)
def test_multiple_instances(code, message):
    # Expanded parameterized tests
    details = ErrorDetails(code=code, message=message)
    assert details.code == code
    assert details.message == message
