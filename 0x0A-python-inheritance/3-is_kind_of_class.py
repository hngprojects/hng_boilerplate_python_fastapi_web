#!/usr/bin/python3
"""
tells if an object is derived or is from a given class
"""


def is_kind_of_class(obj, a_class):
    """
    if obj is an instance of or if the object is an instance of class inherited
    from the specified class returb True else return false
    """
    return (isinstance(obj, a_class))
