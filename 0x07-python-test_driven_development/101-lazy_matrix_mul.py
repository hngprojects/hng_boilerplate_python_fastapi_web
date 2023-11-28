#!/usr/bin/python3

"""a module to multiply matrices using numpy"""
import numpy as np


def lazy_matrix_mul(m_a, m_b):
    """a function to multiply two matrices.

    ARG:
    m_a the first matrix
    m_b the second matrix

    Return:
    result of multiplying the matrix
    """
    return (np.matmul(m_a, m_b))
