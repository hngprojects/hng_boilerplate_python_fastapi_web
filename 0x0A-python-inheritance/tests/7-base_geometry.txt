The ``7-base_geometry`` module
==============================

Using ``BaseGeometry``
----------------------

Importing class from the module:
    >>> BaseGeometry = __import__('7-base_geometry').BaseGeometry


Trying to print the area
    >>> bg = BaseGeometry()
    >>> bg.area()
    Traceback (most recent call last):
    	      ...
    Exception: area() is not implemented


Trying to pass a non-integer argument
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("name", "5")
    Traceback (most recent call last):
    	      ...
    TypeError: name must be an integer


Trying to pass a boolean value
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("name", True)
    Traceback (most recent call last):
    	      ...
    TypeError: name must be an integer


Trying to pass a negative value
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("name", -5)
    Traceback (most recent call last):
    	      ...
    ValueError: name must be greater than 0


Trying to pass a zero value
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("name", 0)
    Traceback (most recent call last):
    	      ...
    ValueError: name must be greater than 0


Passing a positive value
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("name", 5)


Passing one argument to integer_validator
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("name")
    Traceback (most recent call last):
    	      ...
    TypeError: integer_validator() missing 1 required positional argument: 'value'

Integer_validator with no arguments
    >>> bg = BaseGeometry()
    >>> bg.integer_validator()
    Traceback (most recent call last):
    	      ...
    TypeError: integer_validator() missing 2 required positional arguments: 'name' and 'value'


Passing three arguments to integer_validator
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("name", 1, 2)
    Traceback (most recent call last):
    	      ...
    TypeError: integer_validator() takes 3 positional arguments but 4 were given


Passing one argument to area method
    >>> bg = BaseGeometry()
    >>> bg.area(5)
    Traceback (most recent call last):
    	      ...
    TypeError: area() takes 1 positional argument but 2 were given

Passing two arguments to area method
    >>> bg = BaseGeometry()
    >>> bg.area(5, 5)
    Traceback (most recent call last):
    	      ...
    TypeError: area() takes 1 positional argument but 3 were given

Passing tuple to method
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("age", (4,))
    Traceback (most recent call last):
    	      ...
    TypeError: age must be an integer


Passing list to method
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("age", [3])
    Traceback (most recent call last):
    	      ...
    TypeError: age must be an integer


Passing dict to method
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("age", {3, 4})
    Traceback (most recent call last):
              ...
    TypeError: age must be an integer


Passing None to method
    >>> bg = BaseGeometry()
    >>> bg.integer_validator("age", None)
    Traceback (most recent call last):
              ...
    TypeError: age must be an integer
