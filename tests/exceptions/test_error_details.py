import pytest
from metacogitor.exceptions import ErrorDetails
from pydantic import ValidationError

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
