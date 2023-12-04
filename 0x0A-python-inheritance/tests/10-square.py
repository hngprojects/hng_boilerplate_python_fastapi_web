#!/usr/bin/python3

"""a class that inherits from the rectangle"""
Rectangle = __import__("9-rectangle").Rectangle


class Square(Rectangle):
    """defines a square
    """
    def __init__(self, size):
        """innitializes the square"""
        self.integer_validator("size", size)
        super().__init__(size, size)
        self.__size = size
