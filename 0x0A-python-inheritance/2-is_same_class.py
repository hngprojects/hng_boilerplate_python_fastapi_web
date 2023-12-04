#!/usr/bin/python3
"""
a module to compare if an element belongs to a certain class
"""


def is_same_class(obj, a_class):
    """
    distinguishes the class of an object

    args:
    obj - the object
    a_class - the class to check against the object

    return:
    returns true if the object is of the given class else false
    """
    if type(obj) == a_class:
        return (True)
    return (False)
