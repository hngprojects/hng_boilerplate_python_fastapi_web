#!/usr/bin/python3

def search_replace(my_list, search, replace):
    if my_list is None:
        my_list = []

    new_list = my_list[:]

    length = len(new_list)
    for i in range(length):
        if (new_list[i] == search):
            new_list[i] = replace
    return (new_list)
