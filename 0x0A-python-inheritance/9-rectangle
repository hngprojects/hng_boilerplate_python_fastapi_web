#!/usr/bin/python3
"""an inheritance module rectangle"""
BaseGeometry = __import__("7-base_geometry").BaseGeometry


class Rectangle(BaseGeometry):
    """an inheritance class Rectangle"""

    def __init__(self, width, height):
        BaseGeometry.integer_validator(self, "height", height)
        self.__height = height
        BaseGeometry.integer_validator(self, "width", width)
        self.__width = width

    def area(self):
        """a method that calculates the area using the
        width and the height"""
        return (self.__width * self.__height)

    def __str__(self):
        return ("[Rectangle] {}/{}".format(self.__width, self.__height))
