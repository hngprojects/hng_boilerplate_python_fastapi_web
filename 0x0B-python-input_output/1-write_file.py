#!/usr/bin/python3
"""
a function that writes a string to a text file
"""


def write_file(filename="", text=""):
    """
    function writes to a file


    Args:
            filename - filenmae
            text - text to write

    return:
            number of characters written

    """
    with open(filename, mode="w", encoding="utf8") as files:
        new = files.write(text)

    return new
