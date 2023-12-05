#!/usr/bin/python3
"""
a function that reads from a file and prints it to standard output
"""


def read_file(filename=""):
    """
    a function that reads and printts

    Args:
            filename - the path to the file

    return:
            nothing
    """
    with open(filename, mode="r", encoding="utf-8") as files:
        for line in files:
            print(line, end="")
