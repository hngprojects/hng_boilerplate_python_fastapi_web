#!/usr/bin/python3

""" A module to multiply  a matrix"""


def matrix_mul(m_a, m_b):
    """
    a function to multiply a matrix
    m_a: the fist matrix
    m_b: the second matrix

    returns the multiplied matrix

    raises an exception when:

    m_b or m_a is not a list

    m_b or m_a is not a list of list

    if m_b or m_a is empty

    if one of the elements is not a int or float

    if m_a or m_b is not a rectangle
    """

    if not isinstance(m_a, list):
        raise TypeError("m_a must be a list")

    if not isinstance(m_b, list):
        raise TypeError("m_b must be a list")

    for a in m_a:
        if not isinstance(a, list):
            raise TypeError("m_a must be a list of lists")

    for b in m_b:
        if not isinstance(b, list):
            raise TypeError("m_b must be a list of lists")

    if len(m_a) == 0 or (len(m_a) == 1 and len(m_a[0]) == 0):
        raise ValueError("m_a can't be empty")

    if len(m_b) == 0 or (len(m_b) == 1 and len(m_b[0]) == 0):
        raise ValueError("m_b can't be empty")

    for a in m_a:
        for e in a:
            if not isinstance(e, (float, int)):
                raise TypeError("m_a should contain only integers or floats")

    for b in m_b:
        for c in b:
            if not isinstance(c, (float, int)):
                raise TypeError("m_b should contain only integers or floats")

    length = 0

    for a in m_a:
        if length != 0 and len(a) != length:
            raise TypeError("each row of m_a must be of the same size")
        length = len(a)

    length = 0

    for b in m_b:
        if length != 0 and len(b) != length:
            raise TypeError("each row of m_b must be of the same size")
        length = len(b)

    if len(m_a[0]) != len(m_b):
        raise ValueError("m_a and m_b can't be multiplied")

    main = [[0 for _ in range(len(m_b[0]))] for _ in range(len(m_a))]

    for i in range(len(m_a)):
        for j in range(len(m_b[0])):
            for k in range(len(m_b)):
                main[i][j] += m_a[i][k] * m_b[k][j]

    return (main)
