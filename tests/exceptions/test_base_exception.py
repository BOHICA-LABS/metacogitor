# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/19 23:08
@Author  : Joshua Magady
@File    : test_base_exception.py
@Desc    : This tests the base_exception.
"""

import pytest
from metacogitor.exceptions import BaseError
from pydantic import BaseModel


class ErrorModel(BaseModel):
    transaction_id: str = None
    code: str
    message: str


def test_base_error():
    error = ErrorModel(code="123", message="Some error")
    err = BaseError(error)

    assert isinstance(err, Exception)
    assert err.error == error
    assert str(err) == "123 - Some error"


def test_base_error_with_id():
    error = ErrorModel(transaction_id="TX123", code="456", message="Another error")
    err = BaseError(error)

    assert str(err) == "TX123 - 456 - Another error"


@pytest.mark.parametrize(
    "code,message", [("001", "First test error"), ("002", "Second test error")]
)
def test_base_error_multiple(code, message):
    error = ErrorModel(code=code, message=message)
    err = BaseError(error)

    assert str(err) == f"{code} - {message}"
