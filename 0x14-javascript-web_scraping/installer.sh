#!/bin/bash

# Check if package_names.txt exists
if [ ! -f "package_names.txt" ]; then
    echo "Error: package_names.txt not found."
    exit 1
fi

# Read each package name from package_names.txt and attempt installation
while IFS= read -r package; do
    echo "Attempting to install package: $package"
    sudo apt install "$package"
    # Check installation status
    if [ $? -eq 0 ]; then
        echo "Package $package installed successfully."
    else
        echo "Failed to install package: $package"
    fi
done < "package_names.txt"

