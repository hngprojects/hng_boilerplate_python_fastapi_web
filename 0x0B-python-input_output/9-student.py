#!/usr/bin/python3
"""
a class student
"""


class Student:
    """
    a student class
    """
    def __init__(self, first_name, last_name, age):
        """
        innitializez names and age of the student

        Args:

        first_name - the first name of the student

        last_name - the last name of the student

        age - the age of the student
        """
        self.first_name = first_name
        self.last_name = last_name
        self.age = age

    def to_json(self):
        """
        returns a dictionary representation of self
        """
        return self.__dict__.copy()
