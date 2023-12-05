#!/usr/bin/python3

"""
function writes to a file using json repr
"""
import json



def save_to_json_file(my_obj, filename):
    """
    function write to a file using json repr

    Args:
        my_obj - python object
        filename - name of the file

    return:
        nothing
    """
    with open(filename, "w", encoding="utf-8") as files:
        json.dump(my_obj, files)

