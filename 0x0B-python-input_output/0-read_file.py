#!/usr/bin/python3
"""
function reads a text file and prints it
"""


def read_file(filename=""):
    """
    function reads a textfile and prints it to stdout

    args:

    @filename:
    the filename
    """

    with open(filename, "r", encoding='UTF-8') as files:
        print(files)

