#!/usr/bin/python3
"""
a function that appends a string at the end to a text file
"""


def append_write(filename="", text=""):
    """
    function writes to a file


    Args:
            filename - filenmae
            text - text to write

    return:
            number of characters written

    """
    with open(filename, mode="a", encoding="utf8") as files:
        new = files.write(text)

    return new
