#!/usr/bin/python3
"""
function reads a text file and prints it
"""


def read_file(filename=""):
    """
    function reads a textfile and prints it to stdout

    Args:
            filename - the filename

    return:
            nothing
    """

    with open(filename, mode="r", encoding='utf-8') as files:
        for line in files:
            print(files, end="")

