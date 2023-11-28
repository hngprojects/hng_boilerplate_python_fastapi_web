The ``101-lazy_matrix_mul`` module
============================

Using ``lazy_matrix_mul``
---------------------

Importing function from the module:

    >>> matrix_mul = __import__('101-lazy_matrix_mul').lazy_matrix_mul

Multiplying two matrices

    >>> matrix_mul([[1, 2], [3, 4]], [[1, 2], [3, 4]])
    array([[ 7, 10],
     	   [15, 22]])

Multiplying two matrices 2

    >>> matrix_mul([[1, 2]], [[3, 4], [5, 6]])
    array([[13, 16]])

Multiplying two matrices 3

    >>> list1 = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    >>> list2 = [[1, -1, 2], [2, -1, 2], [3, -3, 0]]
    >>> matrix_mul(list1, list2)
    array([[ 30, -26,  10],
           [ 36, -31,  14],
           [ 42, -36,  18]])

Multiplying two matrices 4

    >>> matrix_mul([[1, 5, 7]], [[3], [5], [8]])
    array([[84]])

Passing None as a matrix

    >>> matrix_mul(None, None)
    Traceback (most recent call last):
    	      ...
    TypeError: Object arrays are not currently supported

Passing None as a matrix

    >>> matrix_mul([[7, 12]], None)
    Traceback (most recent call last):
    	      ...
    TypeError: Object arrays are not currently supported

Passing a tuple as a matrix

    >>> matrix_mul((1, 3, 5), [[1.3], [5.2], [7.7]])
    array([55.4])

Passing a string as a matrix

    >>> matrix_mul([[3, 3], [4, 4]], "Holberton")
    Traceback (most recent call last):
    	      ...
    ValueError: Scalar operands are not allowed, use '*' instead

Passing a list of tuples

   >>> matrix_mul([(1, 5, 10)], [(1), (5)])
   Traceback (most recent call last):
   	     ...
   ValueError: shapes (1,3) and (2,) not aligned: 3 (dim 1) != 2 (dim 0)

Passing a list of string

   >>> matrix_mul([[]], ["Holberton"])
   Traceback (most recent call last):
   	     ...
   ValueError: shapes (1,0) and (1,) not aligned: 0 (dim 1) != 1 (dim 0)

Passing an empty matrix

    >>> matrix_mul([], [[1]])
    Traceback (most recent call last):
    	      ...
    ValueError: shapes (0,) and (1,1) not aligned: 0 (dim 0) != 1 (dim 0)

Passing an empty matrix 2

    >>> matrix_mul([[1, 2]], [[]])
    Traceback (most recent call last):
    	      ...
    ValueError: shapes (1,2) and (1,0) not aligned: 2 (dim 1) != 1 (dim 0)

Passing a matrix with a list of strings

    >>> matrix_mul([[1, '1', 1], ['2', 2, '2']], [[3], [3]])
    Traceback (most recent call last):
    	      ...
    ValueError: shapes (2,3) and (2,1) not aligned: 3 (dim 1) != 2 (dim 0)

Passing a matrix with a list of strings 2

    >>> matrix_mul([[2, 4, 6], [3, 6, 9]], [[1], ['2'], [3]])
    Traceback (most recent call last):
    	      ...
    TypeError: invalid data type for einsum

Passing a matrix with an empty list

    >>> matrix_mul([[12, 12, 12], [], [14, 14, 14]], [[2], [3], [8]])
    Traceback (most recent call last):
    	      ...
    ValueError: setting an array element with a sequence.

Passing a matrix which its rows have different size

    >>> matrix_mul([[2, 2, 2], [4, 4, 4]], [[2], [3, 3]])
    Traceback (most recent call last):
    	      ...
    ValueError: setting an array element with a sequence.

Passing two matrix that can't be multiplied

    >>> matrix_mul([[5, 2, 3], [7, 13, 2], [1, 0, 3]], [[2, 3], [6, 9]])
    Traceback (most recent call last):
    	      ...
    ValueError: shapes (3,3) and (2,2) not aligned: 3 (dim 1) != 2 (dim 0)

Missing one argument

    >>> matrix_mul([[1, 2]])
    Traceback (most recent call last):
    	            ...
    TypeError: lazy_matrix_mul() missing 1 required positional argument: 'm_b'

Missing arguments

    >>> matrix_mul()
    Traceback (most recent call last):
    	            ...
    TypeError: lazy_matrix_mul() missing 2 required positional arguments: 'm_a' and 'm_b'
