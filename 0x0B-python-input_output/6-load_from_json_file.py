#!/usr/bin/python3
"""
function that creates an object from a JSON file
"""


def load_from_json_file(filename):
    """
    function that creates an object fron a JSON file

    Args:
        filename -  filename

    return:
        nothing

    """
    import json

    with open(filename, mode="r", encoding="utf8") as files:
        new = json.load(files)

    return new
