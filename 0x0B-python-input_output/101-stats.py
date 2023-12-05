#!/usr/bin/python3
"""Reads from standard input and computes metrics.

After every ten lines or the input of a keyboard interruption (CTRL + C),
prints the following statistics:
    - Total file size up to that point.
    - Count of read status codes up to that point.
"""

if __name__ == "__main__":
    try:
        import sys

        size = 0
        i = 0

        sc = [200, 301, 400, 401, 403, 404, 405, 500]

        ls = {code: 0 for code in sc}

        for line in sys.stdin:
            if i == 10:
                print(size)
