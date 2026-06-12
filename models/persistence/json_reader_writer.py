import json
from pathlib import Path


def write_object_to_file(file_path: Path, output_data: list[dict | None]) -> None:
    """Given a list of objects, write them to a file"""
    file_path.write_text(json.dumps(output_data, indent=2))


def read_object_from_file(file_path: Path) -> list[dict | None]:
    """Given a file path, read and return a list of objects"""
    if file_path.is_file():
        return json.loads(file_path.read_text())
    return []
