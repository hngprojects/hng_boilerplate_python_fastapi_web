
def clone_object(obj: dict, unwanted_fields=[]):
    new_obj = {}
    for k in list(obj.keys()):
        if k in unwanted_fields:
            continue

        new_obj[k] = obj[k]
    return new_obj
