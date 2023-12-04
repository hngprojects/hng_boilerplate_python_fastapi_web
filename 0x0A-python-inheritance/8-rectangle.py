#!/usr/bin/python3

"""an inheritance module rectangle"""
BaseGeometry = __import__("7-base_geometry").BaseGeometry


class Rectangle(BaseGeometry):
    """an inheritance class Rectangle"""

    def __init__(self, width, height):
        BaseGeometry.integer_validator(self, "height", height)
        self.__heigt = height
        BaseGeometry.integer_validator(self, "width", width)
        self.__width = width
