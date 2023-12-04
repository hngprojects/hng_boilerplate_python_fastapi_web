#!/usr/bin/python3

"""
lookup - returns a kist of attributes

"""
def lookup(obj):
    """
    function that lists attributes and methods

    args:
    @obj:
    object

    @return:
    list of atts and methods
    """
    return (dir(obj))
