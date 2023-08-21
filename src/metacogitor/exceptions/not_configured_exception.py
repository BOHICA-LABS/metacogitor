# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 23:08
@Author  : Joshua Magady
@File    : not_configured_exception.py
@Desc    : This defines the Error Classes.
"""

from pydantic import BaseModel, validator, ConstrainedInt, ValidationError
from metacogitor.exceptions.error_details import ErrorDetails
from metacogitor.exceptions.base_exception import BaseError

__ALL__ = ["NotConfiguredException"]


class NotConfiguredException(BaseError):
    """Exception for configuration errors.

    Attributes:
        message (str): Explanation of the error.
    """

    def __init__(self, **kwargs):
        """Initialize the exception."""
        try:
            self.error = ErrorDetails(**kwargs)
        except ValidationError as e:
            raise ValueError("Invalid error details") from e

        super().__init__(self.error)
