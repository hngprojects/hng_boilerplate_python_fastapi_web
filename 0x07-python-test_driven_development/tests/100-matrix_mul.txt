The ``100-matrix_mul`` module
============================

Using ``matrix_mul``
---------------------

Importing function from the module:

    >>> matrix_mul = __import__('100-matrix_mul').matrix_mul

Multiplying two matrices

    >>> matrix_mul([[1, 2], [3, 4]], [[1, 2], [3, 4]])
    [[7, 10], [15, 22]]

Multiplying two matrices 2

    >>> matrix_mul([[1, 2]], [[3, 4], [5, 6]])
    [[13, 16]]

Multiplying two matrices 3

    >>> list1 = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    >>> list2 = [[1, -1, 2], [2, -1, 2], [3, -3, 0]]
    >>> matrix_mul(list1, list2)
    [[30, -26, 10], [36, -31, 14], [42, -36, 18]]

Multiplying two matrices 4

    >>> matrix_mul([[1, 5, 7]], [[3], [5], [8]])
    [[84]]

Passing None as a matrix

    >>> matrix_mul(None, None)
    Traceback (most recent call last):
    	      ...
    TypeError: m_a must be a list

Passing None as a matrix

    >>> matrix_mul([[7, 12]], None)
    Traceback (most recent call last):
    	      ...
    TypeError: m_b must be a list

Passing a tuple as a matrix

    >>> matrix_mul((1, 3, 5), [[1.3], [5.2], [7.7]])
    Traceback (most recent call last):
    	      ...
    TypeError: m_a must be a list

Passing a string as a matrix

    >>> matrix_mul([[3, 3], [4, 4]], "Holberton")
    Traceback (most recent call last):
    	      ...
    TypeError: m_b must be a list

Passing a list of tuples

   >>> matrix_mul([(1, 5, 10)], [(1), (5)])
   Traceback (most recent call last):
   	     ...
   TypeError: m_a must be a list of lists

Passing a list of string

   >>> matrix_mul([[]], ["Holberton"])
   Traceback (most recent call last):
   	     ...
   TypeError: m_b must be a list of lists

Passing an empty matrix

    >>> matrix_mul([], [[1]])
    Traceback (most recent call last):
    	      ...
    ValueError: m_a can't be empty

Passing an empty matrix 2

    >>> matrix_mul([[1, 2]], [[]])
    Traceback (most recent call last):
    	      ...
    ValueError: m_b can't be empty

Passing a matrix with a list of strings

    >>> matrix_mul([[1, '1', 1], ['2', 2, '2']], [[3], [3]])
    Traceback (most recent call last):
    	      ...
    TypeError: m_a should contain only integers or floats

Passing a matrix with a list of strings 2

    >>> matrix_mul([[2, 4, 6], [3, 6, 9]], [[1], ['2'], [3]])
    Traceback (most recent call last):
    	      ...
    TypeError: m_b should contain only integers or floats

Passing a matrix with an empty list

    >>> matrix_mul([[12, 12, 12], [], [14, 14, 14]], [[2], [3], [8]])
    Traceback (most recent call last):
    	      ...
    TypeError: each row of m_a must be of the same size

Passing a matrix which its rows have different size

    >>> matrix_mul([[2, 2, 2], [4, 4, 4]], [[2], [3, 3]])
    Traceback (most recent call last):
    	      ...
    TypeError: each row of m_b must be of the same size

Passing two matrix that can't be multiplied

    >>> matrix_mul([[5, 2, 3], [7, 13, 2], [1, 0, 3]], [[2, 3], [6, 9]])
    Traceback (most recent call last):
    	      ...
    ValueError: m_a and m_b can't be multiplied

Missing one argument

    >>> matrix_mul([[1, 2]])
    Traceback (most recent call last):
    	      ...
    TypeError: matrix_mul() missing 1 required positional argument: 'm_b'

Missing arguments

    >>> matrix_mul()
    Traceback (most recent call last):
    	      ...
    TypeError: matrix_mul() missing 2 required positional arguments: 'm_a' and 'm_b'
