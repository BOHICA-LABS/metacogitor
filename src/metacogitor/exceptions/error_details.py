# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/19 23:08
@Author  : Joshua Magady
@File    : error_details.py
@Desc    : This defines the ErrorDetails Classes.
"""
from pydantic import BaseModel, root_validator, conint
from pydantic.types import ConstrainedInt

from typing import Optional

__ALL__ = ["ErrorDetails"]


class ErrorDetails(BaseModel):
    """Error details class.

    This class is used to define the error details.

    Attributes:
        message (str): The error message.
        code (int): The error code.
    """

    # TODO: remove default message value and code value (After updating all errors)
    message: str = "The required configuration is not set"
    """The error message."""

    # TODO: remove default message value and code value (After updating all errors)
    code: conint(ge=100, le=1000, multiple_of=1) = 100
    """The error code."""

    transaction_id: Optional[str] = None
    """The transaction id."""

    @root_validator
    def check_fields_set(cls, values):
        """Check that the required fields are set."""

        message = values.get("message")
        code = values.get("code")

        if message is None or code is None:
            raise ValueError("message and code are required")

        return values
