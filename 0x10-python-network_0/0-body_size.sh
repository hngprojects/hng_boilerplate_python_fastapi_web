#!/usr/bin/env bash
# Scriot sends a request to a given URL
# Check if URL argument is provided
if [ $# -ne 1 ]; then
	echo "Usage: $0 <URL>"
        exit 1
fi

# Send request to the URL using curl and store response body in a temporary file
response=$(curl -s -o /tmp/response_body "$1")

# Check if curl request was successful
if [ $? -ne 0 ]; then
	echo "Error: Failed to send request to $1"
	exit 1
fi

# Get the size of the response body in bytes and display it
body_size=$(wc -c < /tmp/response_body)
echo "$body_size"

# Clean up temporary file
rm -f /tmp/response_body
