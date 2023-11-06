#include <Python.h>
#include <stdio.h>
/**
 * print_python_list_info - pints a python list info from c
 * @p: Python object
 * Return: nothing
 */
void print_python_list_info(PyObject *p)
{
	long int list;
	PyListObject *lt;
	PyObject *element;
	int i;

	list = PyList_Size(p);
	lt = (PyListObject *)p;
	printf("[*] Size of the Python List = %ld\n", list);
	printf("[*] Allocated = %ld\n", lt->allocated);

	for (i = 0; i < Py_SIZE(p); i++)
	{
		element = PyList_GetItem(p, i);
		printf("Element %d: %s\n", i, Py_TYPE(element)->tp_name);
	}
}
