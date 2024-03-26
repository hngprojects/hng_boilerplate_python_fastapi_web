#!/bin/bash

# Read package names from the file
packages_file="package_names.txt"  # Replace with your actual filename
while IFS= read -r package_name; do
    # Remove package with force (caution!)
    sudo dpkg --remove --force-all "$package_name"
done < "$packages_file"

echo "Package removal completed (with force)."
