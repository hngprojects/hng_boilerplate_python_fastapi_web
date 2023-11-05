#!/usr/bin/python3
def no_c(my_string):
    new_str = ""

    lenn = len(my_string)

    for i in range(lenn):
        if ((my_string[i] != 'c') and (my_string[i] != 'C')):
            new_str += my_string[i]
    return new_str
