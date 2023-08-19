# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 23:08
@Author  : Joshua Magady
@File    : errors.py
@Desc    : This defines the Error Classes.
"""

__ALL__ = ["NotConfiguredException"]


class NotConfiguredException(Exception):
    """Exception for configuration errors.

    Attributes:
        message (str): Explanation of the error.
    """

    def __init__(self, message="The required configuration is not set"):
        """Initialize the exception with a custom message."""
        self.message = message
        super().__init__(self.message)
