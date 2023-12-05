#!/usr/bin/python3
import json
"""
function that seriarizes an object and returns it
"""


def to_json_string(my_obj):
    """
    this fucn seriarizes a python object and returns a json string

    Args:
        my_obj - python object

    return:
        a json string
    """
    return (json.dumps(my_obj))
