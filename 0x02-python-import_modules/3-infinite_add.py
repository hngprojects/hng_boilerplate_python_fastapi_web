#!/usr/bin/python3
if __name__ == "__main__":
    import sys

    length = len(sys.argv)
    if (length == 1):
        print("{}".format(0))
    i = 0
    count = 0
    for a in (sys.argv):
        if (i != 0):
            count += int(a)
        i += 1
    if (length >= 2):
        print("{}".format(count))
