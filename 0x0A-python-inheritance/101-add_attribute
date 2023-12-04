#!/usr/bin/python3
"""
a funtion to set new attribute
"""


def add_attribute(obj, attr_name, attr_value):
    """
    Adds a new attribute to an object if it's possible.

    Args:
        obj: The object to which the attribute should be added.
        attr_name (str): The name of the new attribute.
        attr_value: The value of the new attribute.

    Raises:
        TypeError: If the object can't have a new attribute.
    """

    if "__dict__" not in dir(obj) or "slots" in dir(obj):
        raise TypeError("can't add new attribute")

    setattr(obj, attr_name, attr_value)
