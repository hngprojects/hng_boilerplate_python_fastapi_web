#!/bin/bash
# Send request to the URL using curl, display only the status code
#awk 'NR==1{printf "%s", $2}' test7 $(curl -sI "$1" -o test7)
status_code=$(curl -sI "$1" | awk 'NR==1{print $2}')
echo "$status_code"
