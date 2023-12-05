#!/usr/bin/python3
"""
function that deseriarizes a json string and returns it
"""
import json


def from_json_string(my_str):
    """
    this fucn deseriarizes a string and returns a python object

    Args:
        my_str - string

    return:
        a python object
    """
    return (json.loads(my_str))
