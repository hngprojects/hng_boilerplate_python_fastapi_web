#!/usr/bin/python3
"""
module reads input, put it into a list,
convert the list to JSON, and store it in a file.
"""
if __name__ == "__main__":
    from sys import argv
    load_from_json = __import__("6-load_from_json_file").load_from_json_file
    save_to_json = __import__("5-save_to_json_file").save_to_json_file

    try:
        new = load_from_json("add_item.json")
    except FileNotFoundError:
        new = []

    new.extend(argv[1:])

    save_to_json(new, "add_item.json")
