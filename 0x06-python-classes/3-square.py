#!/usr/bin/python3

"""class that dfines a square"""


class Square:
    """initialization"""

    def __init__(self, size=0):

        """instantation"""
        if not isinstance(size, int):
            raise TypeError("size must be an integer")
        if size < 0:
            raise ValueError("size must be >= 0")
        self.__size = size

        """calculating the area of the square"""
    def area(self):
        """returning the current area os the square"""
        return self.__size ** 2
