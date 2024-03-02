#!/bin/bash

# Check if URL argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi
touch response.txt
# Send request and save response to a temporary file
curl -s -o response.txt -w "%{http_code}" "$1"

# Extract status code from the response file
status_code=$(cat response.txt)

# Display the status code
echo "Status code: $status_code"

# Clean up temporary file
rm -f response.txt
