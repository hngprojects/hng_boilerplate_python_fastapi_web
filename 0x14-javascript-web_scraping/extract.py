import sys
import re

def extract_node_packages(input_file, output_file):
    # Regular expression pattern to match package names and versions
    pattern = r'\bnode-\w+\b(?:\s*\(.*?\))?'
    packages = set()

    # Open the input file and read its contents
    with open(input_file, 'r') as f:
        content = f.read()

        # Find all matches of the pattern in the content
        matches = re.findall(pattern, content)

        # Add matched packages to the set
        for match in matches:
            packages.add(match.strip())

    # Write package names to the output file
    with open(output_file, 'w') as f:
        for package in packages:
            f.write(f"{package}\n")

if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Extract node packages from the input file and write to the output file
    extract_node_packages(input_file, output_file)
