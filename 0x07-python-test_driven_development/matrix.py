#!/usr/bin/python3
"""
Module divides all elements of a matrix
and returns a new matrix with divided contents
"""


def matrix_divided(matrix, div):
    """
    function divides content of a matrix
    """
    message = "matrix must be a matrix (list of lists) of integers/floats"
    if type(matrix) is not list or not matrix[0] or not matrix[1]:
        raise TypeError(message)
    if len(matrix[0]) != len(matrix[1]):
        raise TypeError("Each row of the matrix must have the same size")
    if not isinstance(div, (int, float)):
        raise TypeError("div must be a number")
    if div == 0:
        raise ZeroDivisionError("division by zero")

    new = [list(row) for row in matrix]

    j = 0
    i = 0

    while (i < len(matrix)):
        while (j < len(matrix[0])):
            if not isinstance(matrix[i][j], (int, float))\
                    or not isinstance(matrix[i], list):
                raise TypeError(message)
            new[i][j] = round((matrix[i][j] / div), 2)
            j = j + 1
        j = 0
        i = i + 1
    return new
