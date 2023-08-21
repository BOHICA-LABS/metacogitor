# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/19 23:08
@Author  : Joshua Magady
@File    : base_exception.py
@Desc    : This defines the BaseError Class.
"""
from pydantic import BaseModel

__ALL__ = ["BaseError"]


class BaseError(Exception):
    """
    Exception for configuration errors.

    Base class for all exceptions.

    Attributes:
        error (BaseModel): The error details.
        message (str): Explanation of the error.
    """

    def __init__(self, error: BaseModel):
        """Initialize the exception."""

        self.error = error
        super().__init__(error.message)

    def __str__(self):
        """Return the error message."""

        if hasattr(self.error, "transaction_id"):
            if self.error.transaction_id:
                return f"{self.error.transaction_id} - {self.error.code} - {self.error.message}"

        return f"{self.error.code} - {self.error.message}"
