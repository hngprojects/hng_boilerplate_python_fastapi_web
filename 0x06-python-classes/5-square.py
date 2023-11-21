#!/usr/bin/python3

"""defining a square class"""


class Square:
    """initializing size"""

    def __init__(self, size=0):
        self.size = size

    """property to retrieve it"""

    @property
    def size(self):
        return self.__size

    """instantation"""

    @size.setter
    def size(self, value):
        if not isinstance(value, int):
            raise TypeError("size must be an integer")
        if value < 0:
            raise ValueError("size must be >= 0")

        self.__size = value

    """calculating the area of a square"""

    def area(self):
        return self.__size ** 2

    """printing self"""

    def my_print(self):
        if self.__size == 0:
            print()
        else:
            for _ in range(self.__size):
                print("#" * self.__size)
