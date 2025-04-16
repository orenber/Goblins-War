import enum
import os
from typing import List, Tuple, Set, Union


def full_file(file_folder: List[str] = None) -> str:
    """
    Constructs an absolute path from a list of path components.

    Args:
        file_folder: List of path components (e.g., ['folder', 'subfolder', 'file.txt'])

    Returns:
        Absolute path string

    Raises:
        ValueError: If file_folder is None or empty
    """
    if not file_folder:
        raise ValueError("file_folder cannot be empty")
    return os.path.abspath(os.path.join(*file_folder))


def is_member(small: List[str], big: List[str]) -> Tuple[bool, List[str]]:
    """
    Checks if all elements in 'small' list are present in 'big' list.

    Args:
        small: List of items to check
        big: List of items to check against

    Returns:
        Tuple containing:
        - Boolean indicating if all items are present
        - List of missing items (empty if all present)
    """
    small_set = set(small)
    big_set = set(big)
    missing = list(small_set - big_set)
    return small_set.issubset(big_set), missing


class Direction(enum.Enum):
    """
    Enum representing movement directions with associated values.

    Values:
        LEFT: -1
        RIGHT: 1
        DOWN: -1 (vertical axis)
        UP: 1 (vertical axis)
        CENTER: 0 (no movement)
    """
    LEFT = -1
    RIGHT = 1
    DOWN = -1
    UP = 1
    CENTER = 0

    @classmethod
    def from_string(cls, direction_str: str) -> 'Direction':
        """
        Get Direction enum from string representation.

        Args:
            direction_str: String representation of direction (case-insensitive)

        Returns:
            Corresponding Direction enum

        Raises:
            ValueError: If string doesn't match any direction
        """
        try:
            return cls[direction_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid direction: {direction_str}")

    def opposite(self) -> 'Direction':
        """
        Returns the opposite direction.

        Returns:
            Direction enum representing the opposite direction
        """
        if self == Direction.LEFT:
            return Direction.RIGHT
        elif self == Direction.RIGHT:
            return Direction.LEFT
        elif self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        return self


# Additional utility functions that might be helpful
def ensure_directory_exists(path: Union[str, List[str]]) -> str:
    """
    Ensures the directory exists, creating it if necessary.

    Args:
        path: Either a string path or list of path components

    Returns:
        Absolute path to the directory
    """
    if isinstance(path, list):
        path = full_file(path)
    os.makedirs(path, exist_ok=True)
    return path


def normalize_path(path: str) -> str:
    """
    Normalizes a path by resolving relative references and converting to absolute path.

    Args:
        path: Input path string

    Returns:
        Normalized absolute path
    """
    return os.path.abspath(os.path.normpath(os.path.expanduser(path)))


if __name__ == "__main__":
    # Example usage
    print("Path example:", full_file(["dir", "subdir", "file.txt"]))

    # is_member example
    result, missing = is_member(["a", "b"], ["a", "b", "c"])
    print(f"All members: {result}, Missing: {missing}")

    # Direction examples
    print(Direction.from_string("left"))
    print(Direction.LEFT.opposite())
