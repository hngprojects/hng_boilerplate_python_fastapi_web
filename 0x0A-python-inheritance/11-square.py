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

    def __str__(self):
        """
        create a string representation of  the square"""
        return ("[Square] {}/{}".format(self.__size, self.__size))

    def area(self):
        """
        calculates the area of the square
        """
        return (self.__size ** 2)
