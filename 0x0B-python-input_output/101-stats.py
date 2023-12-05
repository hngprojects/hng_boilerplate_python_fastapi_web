#!/usr/bin/python3
import sys

def print_statistics(total_size, status_counts):
    """Print statistics based on current metrics."""
    print("File size: {:d}".format(total_size))
    for status_code in sorted(status_counts.keys()):
        print("{}: {}".format(status_code, status_counts[status_code]))

def main():
    total_size = 0
    status_counts = {}

    try:
        for i, line in enumerate(sys.stdin, 1):
            try:
                parts = line.split()
                size = int(parts[-1])
                status_code = int(parts[-2])

                total_size += size

                if status_code in status_counts:
                    status_counts[status_code] += 1
                else:
                    status_counts[status_code] = 1

                if i % 10 == 0:
                    print_statistics(total_size, status_counts)

            except (ValueError, IndexError):
                # Ignore lines that don't match the expected format
                pass

    except KeyboardInterrupt:
        # Handle Ctrl+C interruption
        print_statistics(total_size, status_counts)

if __name__ == "__main__":
    main()

