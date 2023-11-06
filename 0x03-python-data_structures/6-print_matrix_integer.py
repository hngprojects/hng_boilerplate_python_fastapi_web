#!/usr/bin/python3
def print_matrix_integer(matrix=[[]]):
    if not matrix:
        pass
    else:
        out = len(matrix)
        inn = len(matrix[0])

        for i in range(out):
            for j in range(inn):
                if (j != 0):
                    print(" ", end="")
                print("{:d}".format(matrix[i][j]), end="")
            print()
