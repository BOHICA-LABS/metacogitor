"""Inspect a module and print all classes and functions in it."""
# -*- coding: utf-8 -*-

import inspect

import metacogitor  # replace with your module


def print_classes_and_functions(module):
    """Print all classes and functions in a module.

    FIXME: NOT WORK... yet.

    :param module: The module to inspect.
    :type module: module
    """

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            print(f"Class: {name}")
        elif inspect.isfunction(obj):
            print(f"Function: {name}")
        else:
            print(name)

    print(dir(module))


if __name__ == "__main__":
    print_classes_and_functions(metacogitor)
