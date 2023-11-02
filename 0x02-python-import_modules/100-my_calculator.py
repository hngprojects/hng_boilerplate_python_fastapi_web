#!/usr/bin/python3
if __name__ == "__main__":
    import sys
    from calculator_1 import add, sub, mul, div

    ll = len(sys.argv)
    if ll != 4:
        print("Usage: ./100-my_calculator.py <a> <operator> <b>")
        exit(1)
    else:
        ch = sys.argv[2]

    if (ch == '+' or ch == '-' or ch == '*' or ch == '/'):
        a = int(sys.argv[1])
        b = int(sys.argv[3])
        if ch == '+':
            print("{} + {} = {}".format(a, b, add(a, b)))
        if ch == '-':
            print("{} - {} = {}".format(a, b, sub(a, b)))
        if ch == '*':
            print("{} * {} = {}".format(a, b, mul(a, b)))
        if ch == '/':
            print("{} / {} = {}".format(a, b, div(a, b)))
    else:
        print("Unknown operator. Available operators: +, -, * and /")
        exit(1)
