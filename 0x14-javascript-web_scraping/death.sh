#!/bin/bash

# Check if the file containing package names is provided as an argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <package_list_file>"
    exit 1
fi

# Verify if the file exists
if [ ! -f "$1" ]; then
    echo "Error: File '$1' not found."
    exit 1
fi

# Loop through each package name in the file
while IFS= read -r package; do
    # Remove the package using sudo apt remove
    sudo apt remove "$package"
done < "$1"

echo "Packages removed successfully."
