#!/usr/bin/python3
"""
a module to  read  a file and print it to the standard output
"""


def read_file(filename=""):
    """
    a function to read and print a file

    Args:
            filename - the path to the file

    return:
            nothing
    """
    with open(filename, mode="r", encoding="utf-8") as files:
        for line in files:
            print(line, end="")
