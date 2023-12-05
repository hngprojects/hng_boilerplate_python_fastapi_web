#!/usr/bin/python3
"""
a module to insert text incase of an occurence of a given text
the text is inserted in the line that follows the text occurence
"""


def append_after(filename="", search_string="", new_string=""):
    """
    a function that inserts a line of text to a file,
    after each line containing a specific string

    ARGS

    filname - (file)the name of the file to read from

    search_string - (string) the string to search for

    new_string - (string) the string to insert if an occurence of the
    the search string was found
    """
    with open(filename, mode="r+", encoding="utf-8") as file:
        content = ""

        for line in file:
            content += line
            if search_string in line:
                content += new_string
        file.seek(0)
        file.write(content)
