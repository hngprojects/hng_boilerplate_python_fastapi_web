#!/usr/bin/python3

"""

A module that adds two numbers

"""

def add_integer(a, b=98):
    """
    Adds two numbers

    Args:
    a:first number
    b:the second number

    Returns:
    addition of those two numbers

    raises a TypeError if a and b are not int or float
    >>> add_integer(2, 5)
    7

    >>> add_integer(3, 5)
    8
    """

    if not isinstance(a, (float, int)):
        raise TypeError("a must be an integer")

    elif not isinstance(b, (float, int)):
        raise TypeError("b must be an integer")
    if isinstance(a, float):
        a = int(a)
    if isinstance(b, float):
        b = int(b)

    return (a + b)
