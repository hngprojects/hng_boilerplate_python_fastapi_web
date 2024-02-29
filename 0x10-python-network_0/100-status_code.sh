#!/bin/bash

# Send request to the URL using curl, display only the status code
curl -s -o /dev/null -I -w "%{http_code}" "$1"
