#!/usr/bin/python3
"""
script that takes 2 arguments in order to solve this challenge
"""

import requests
import sys


if __name__ == '__main__':
    url = f'https://api.github.com/repos/{sys.argv[2]}/{sys.argv[1]}/commits'
    headers = {'Accept': 'application/vnd.github+json'}
    r = requests.get(url, headers=headers)
    comm = r.json()
    try:
        for i in range(10):
            print("{}: {}".format(
                comm[i].get("sha"),
                comm[i].get("commit").get("author").get("name")))
    except IndexError:
        pass
