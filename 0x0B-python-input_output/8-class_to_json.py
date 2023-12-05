#!/usr/bin/python3

"""
a module that creates a dictionary from an object for json
serialization
"""


def class_to_json(obj):
    """
    returns an dictionary representation of an object
    """
    if obj.__dict__:
        return (obj.__dict__)
