from __future__ import annotations

import json
from pathlib import Path


def write_object_to_file(file_path: Path, output_data: dict) -> None:
    """Given a list of dict representation of Objects, write them to a file.

    Parameters
    -----------
        file_path: Path
            Location and name to write file to
        output_data: list[dict]
            List of dict representation of Objects to write to file. Refer to to_dict() methods

    Raises
    -----------
        FileNotFoundError
            When the parent directory of file_path is not a valid directory
        IsADirectoryError
            When the file_path is a directory instead of a file

    """
    if not file_path.parent.is_dir():
        raise FileNotFoundError(f"{file_path.parent} is not a directory")
    if file_path.is_dir():
        raise IsADirectoryError(f"{file_path} is a directory not a writable file")

    file_path.write_text(json.dumps(output_data, indent=2))


def read_object_from_file(file_path: Path) -> dict:
    """Given a file path, read and return a list of dict representation objects.

    Parameters
    -----------
        file_path: Path
            Location and name of file being read from

    Raises
    -----------
        FileNotFoundError
            When the file_path is not a file or not found

    Returns
    -----------
        dict
            List of dict representation of Objects to read from file. Refer to to_dict() methods
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"{file_path} is not a file")

    return json.loads(file_path.read_text())
