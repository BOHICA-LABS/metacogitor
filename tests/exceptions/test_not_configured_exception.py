# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/20 23:08
@Author  : Joshua Magady
@File    : tests_not_configured_exception.py
@Desc    : This defines the tests for NotConfiguredException.
"""

import pytest
from unittest.mock import patch
from metacogitor.exceptions import NotConfiguredException, ErrorDetails


def test_not_configured_exception():
    error = ErrorDetails(code=123, message="Config missing")
    err = NotConfiguredException(code=123, message="Config missing")

    assert isinstance(err, Exception)
    assert err.error.code == 123
    assert err.error.message == "Config missing"


def test_invalid_error_details():
    with pytest.raises(ValueError) as exc_info:
        NotConfiguredException(code="abc")

    assert "Invalid error details" in str(exc_info.value)


@pytest.mark.parametrize("code,message", [(123, "Error 1"), (456, "Error 2")])
def test_multiple_not_configured_errors(code, message):
    err = NotConfiguredException(code=code, message=message)
    assert err.error.code == code
    assert err.error.message == message


def test_base_error_attributes():
    err = NotConfiguredException(code=123, message="Error")
    assert err.error
    assert err.args == ("Error",)


@pytest.mark.parametrize(
    "code,message",
    [(123, "Error 1"), (456, "Error 2"), (789, "Error 3"), (987, "Error 4")],
)
def test_multiple_instances(code, message):
    # Expanded parametrized tests
    err = NotConfiguredException(code=code, message=message)
    assert err.error.code == code
    assert err.error.message == message
