#!/usr/bin/python3
"""
Module posts a request
"""
import sys
import urllib.parse
import urllib.request


if __name__ == '__main__':
    url, email = sys.argv[1:3]
    data = urllib.parse.urlencode({'email': email}).encode('ascii')
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8'))
