#!/usr/bin/python3
"""
takes in a URL and an email address, sends a POST request to the passed URL
with the email as a parameter, and finally displays the body of the response.
"""
import sys
import requests


if __name__ == '__main__':
    url, email = sys.argv[1:3]
    print(requests.post(url, data={'email': email}).text)
