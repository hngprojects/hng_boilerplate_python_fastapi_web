#!/usr/bin/python3
if __name__ == "__main__":
    import sys

    length = len(sys.argv)
    if (length == 1):
        print("{} arguments.".format(length - 1))
    elif (length == 2):
        print("{} argument:\n{}: {}".format(length, length - 1, sys.argv[length - 1]))
    elif (length > 2):
        print("{} arguments:".format(length -1))
        i = 1
        for a in sys.argv[1:]:
            print("{}: {}".format(i, a))
            i += 1
