#!/usr/bin/python3
"""
A matrix division module

"""

def matrix_divided(matrix, div):
    """
    The function matrix_divided divides the input
    matrix(list of lists containing floats or int)

    Args:
    @matrix: a list of list containing floats or int
    @div: the divisor of all the elements of the matrix

    Return: a matrix whose elements are a divisor of div

    Raises an execption when:
    if found an element which is not if type int or float
    if the lists in the matrix are not of equal size
    if div is zero.This raises a zero division error
    """

    lists = ("matrix must be a matrix (list of lists) of integers/floats")
    if not isinstance(div, (int, float)):
        raise TypeError("div must be a number")

    if div == 0:
        raise ZeroDivisionError("division by zero")

    if not isinstance(matrix, list) or not matrix:
        raise TypeError(lists)

    list_length = 0

    for a in matrix:
        if not isinstance(a, list) or not a:
            raise TypeError(lists)

        if list_length != 0 and len(a) != list_length:
            raise TypeError("Each row of the matrix must have the same size")

        for b in a:
            if not isinstance(b, (int, float)):
                raise TypeError(lists)
        list_length = len(a)

    Matrix= list(map(lambda a : list(map(lambda b : round(b / div, 2), a)), matrix))

    return (Matrix)
