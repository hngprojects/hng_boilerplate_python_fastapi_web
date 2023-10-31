#!/usr/bin/python3
def remove_char_at(str, n):
    s = ""
    for i in range(len(str)):
        if i != n:
            s = s + str[i]
    return (s)
