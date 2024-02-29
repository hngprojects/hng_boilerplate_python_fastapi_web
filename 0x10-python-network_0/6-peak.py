#!/usr/bin/python3
"""
Module seeks the peak of a list of numbers
"""
def find_peak(list_of_integers):
    """Find a peak in a list of unsorted integers."""
    if not list_of_integers:
        return None

    low, high = 0, len(list_of_integers) - 1

    while low < higth:
        mid = (low + high) // 2
        if list_of_integers[mid] > list_of_integers[mid + 1]:
            high = mid
        else:
            low = mid + 1

    return list_of_integers[low]
