#!/usr/bin/python3

"""

A module to print the input names given

"""


def say_my_name(first_name, last_name=""):

    """
    A function to print the input names

    @fist_name: the first name
    @second_name: the second name

    Return: Nothing but write the names to standard output
    """

    if not isinstance(first_name, str):
        raise TypeError("first_name must be a string")

    if not isinstance(last_name, str):
        raise TypeError("last_name must be a string")

    print("My name is {} {}".format(first_name, last_name))
