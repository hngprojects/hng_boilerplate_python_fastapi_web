#!/usr/bin/python3

"""
a module to create a list of lists of pascals triangle
"""


def pascal_triangle(n):
    """
    creates pascals triangle in range n


    Args:

    n - (int) the range of the pascals triangle

    return - a list of list of pascals triangle

    """

    if n == 0:
        return ([])

    pascal = [[1]]

    for i in range(1, n):
        row = [1]
        for j in range(1, i):
            row.append(pascal[i - 1][j - 1] + pascal[i - 1][j])
        row.append(1)
        pascal.append(row)
    return pascal
