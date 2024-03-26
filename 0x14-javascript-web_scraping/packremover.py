import subprocess
import sys

def remove_packages(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            package = line.strip()
            if package.startswith("node-"):
                subprocess.run(['npm', 'uninstall', package])

if __name__ == "__main__":
    file_path = sys.argv[1]
    remove_packages(file_path)
