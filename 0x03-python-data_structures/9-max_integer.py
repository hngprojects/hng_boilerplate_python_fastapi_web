#!/usr/bin/python3
def max_integer(my_list=[]):
    if not my_list:
        return None
    else:
        length = len(my_list) - 1
        i = 0
        res = my_list[i]
        while i < length:
            if (res > (my_list[i + 1])):
                pass
            else:
                res = my_list[i + 1]
            i += 1

        return res
