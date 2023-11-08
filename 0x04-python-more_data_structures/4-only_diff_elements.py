#!/usr/bin/python3

def only_diff_elements(set_1, set_2):
    new = {i for i in set_1 if i not in set_2}

    for i in set_2:
        if i not in set_1:
            new.add(i)
    return (new)
