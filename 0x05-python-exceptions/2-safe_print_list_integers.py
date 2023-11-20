def safe_print_list_integers(my_list=[], x=0):
    j = 0
    try:
        for i in range(0, x):
            try:
                print("{:d}".format(my_list[i]), end='')
            except Exception:
                continue
            j += 1
    except Exception:
        pass

    print()
    return j
