# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 23:08
@Author  : Joshua Magady
@File    : debounce.py
@Desc    : This defines the Debounce decorator.
"""
from functools import wraps
from time import perf_counter

__ALL__ = ["debounce"]


def debounce(func=None, wait=1):
    """Decorator that will postpone a functions execution until after wait seconds
    have elapsed since the last time it was invoked."""

    def decorator(fn):
        time_of_last_call = 0

        @wraps(fn)
        def debounced(*args, **kwargs):
            nonlocal time_of_last_call
            now = perf_counter()
            time_since_last_call = now - time_of_last_call

            if time_since_last_call >= wait:
                time_of_last_call = now
                return fn(*args, **kwargs)

        return debounced

    if func is None:
        return decorator
    else:
        return decorator(func)
