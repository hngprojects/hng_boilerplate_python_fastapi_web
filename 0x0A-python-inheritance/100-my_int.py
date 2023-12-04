#!/usr/bin/python3
"""
a subclass MyInt thats inherits from int
"""


class MyInt(int):
    """ Class  that inheriits from int and modifies the equality
    and inequality  magic methods
    """
    def __eq__(self, other):
        """inverting the equality sign"""
        return int(str(self)) != other

    def __ne__(self, other):
        """inverting the inequality sign"""
        return int(str(self)) == other
