

def is_member(small: list, big: list)->bool:
    items = set(big)
    return set(small).issubset(items)
