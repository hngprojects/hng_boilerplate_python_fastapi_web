#!/usr/bin/python3

"""
a module to create a class
"""


class BaseGeometry:
    """
    a new class
    """
    def area(self):
        """
        a method to calculate area
        """
        raise Exception("area() is not implemented")

    def integer_validator(self, name, value):
        """
        validates that a value is an integer

        Args:

        name: the name of the parameter
        value:the value to validate

        raises an exception:

        TypeError: if value is not an integer
        ValueError: if value is less than 0
        """

        if type(value) != int:
            raise TypeError("{} must be an integer".format(name))
        if value <= 0:
            raise ValueError("{} must be greater than 0".format(name))
