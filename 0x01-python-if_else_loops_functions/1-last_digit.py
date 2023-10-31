#!/usr/bin/python3
import random
number = random.randint(-10000, 10000)
num = number % 10
str = (f"Last digit of {number} is {num}")
if (num > 5):
    print(f"{str} and is greater than 5")
elif (num == 0):
    print(f"{str} and is 0")
elif (num < 6 and not 0):
    print(f"{str} and is less than 6 and not 0")

