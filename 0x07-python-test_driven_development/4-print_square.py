#!/usr/bin/python3

"""
A MODULE TO PRINT A SQUARE

"""

def print_square(size):
    """
    this isa function to print a square to
    the standard output.

    @size: the size of the square
    @Return: nothing

    """
    if type(size) is not int:
        raise TypeError("size must be an integer")
    if size <= 0:
        raise ValueError("size must be >= 0")
    if (size // 1) != size:
        raise TypeError("size must be an integer")


    for i in range(0, size):
        for j in range(0, size):
            print("#", end="")
        print()
