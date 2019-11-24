import enum


def is_member(small: list, big: list)->bool:
    items = set(big)
    difference = list(set(small)-set(big))
    member = set(small).issubset(items)
    return member, difference


class Direction(enum.Enum):
    left = -1
    right = 1
    down = -1
    up = 1
    center = 0
