#!/usr/bin/python3
def best_score(dct):
    if dct is None:
        return (None)
    best_key = None
    best_value = 0

    for k, v in dct.items():
        if v > best_value:
            best_key = k
            best_value = v
    return (best_key)
