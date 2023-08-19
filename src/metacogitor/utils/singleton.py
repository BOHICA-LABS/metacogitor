#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 16:15
@Author  : Joshua Magady
@File    : singleton.py
@Desc    : Ensure only one instance of a class.
"""
import abc

__ALL__ = ["Singleton"]


class Singleton(abc.ABCMeta, type):
    """Singleton metaclass to ensure only one instance of a class.

    This metaclass makes use of a private dictionary to store class
    instances. When the class is called, it will return the existing
    instance if one exists, otherwise create a new one.
    """

    _instances = {}
    """Private dictionary to store class instances."""

    def __call__(cls, *args, **kwargs):
        """Call method for the singleton metaclass.

        If an instance for the class does not exist in `_instances`,
        create one. Otherwise return the existing instance.

        Args:
            cls (class): The class being called.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            class instance: The singleton instance for the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
