#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/15/8 12:41
@Author  : Joshua Magady
@File    : logs.py
@Description: This defines the logging configuration for the metacogitor project.
"""

import sys

from loguru import logger as _logger

from metacogitor.const import PROJECT_ROOT


def define_log_level(print_level="INFO", logfile_level="DEBUG"):
    """
    Configure and set the logging levels for the logger.

    :param print_level: Log level for console output.
    :param logfile_level: Log level for writing to the log file.
    :return: Configured logger instance.
    """

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(PROJECT_ROOT / "logs/log.txt", level=logfile_level)
    return _logger


logger = define_log_level()
