import re

import sys  # Added for command-line argument handling
def parse_packages(filename):
  """
  Parses a file containing package information and extracts package names.

  Args:
      filename (str): Path to the file containing package information.

  Returns:
      list: List of unique package names extracted from the file.
  """
  # Regular expression to capture package names
  package_regex = r"node-([a-z\-_]+)"

  try:
    # Open the file for reading
    with open(filename, "r") as file:
      text = file.read()
  except FileNotFoundError:
    print(f"Error: File '{filename}' not found.")
    return []

  # Find all matches of the regex pattern in the text
  matches = re.findall(package_regex, text, re.MULTILINE)

  # Return a list of unique package names
  return set(matches)

def main():
  """
  Main function to handle script execution.
  """
  # Check for command-line arguments
  if len(sys.argv) < 2:
    print("Usage: python parse_packages.py <filename>")
    return

  # Get the filename from the first argument
  filename = sys.argv[1]

  # Extract and write package names
  package_names = parse_packages(filename)

  # Create a new filename with "_parsed" suffix
  new_filename = f"{filename.rsplit('.', 1)[0]}_parsed.txt"

  # Write unique package names to a new file
  try:
    with open(new_filename, "w") as file:
      for package in package_names:
        file.write(f"{package}\n")
    print(f"Package names written to '{new_filename}'")
  except OSError as e:
    print(f"Error writing to file: {e}")

if __name__ == "__main__":
  main()


