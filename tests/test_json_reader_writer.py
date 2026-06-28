import pytest

from src.finance_planning_tool.models.persistence import (
    read_object_from_file,
    write_object_to_file,
)


def test_write_object_to_file(valid_file_path, full_dict_entry):
    write_object_to_file(valid_file_path, full_dict_entry)
    assert valid_file_path.is_file()


def test_write_object_to_file_with_missing_file(invalid_missing_file_path, full_dict_entry):
    with pytest.raises(FileNotFoundError):
        write_object_to_file(invalid_missing_file_path, full_dict_entry)


def test_write_object_to_file_with_dir(invalid_dir_file_path, full_dict_entry):
    with pytest.raises(IsADirectoryError):
        write_object_to_file(invalid_dir_file_path, full_dict_entry)


def test_read_object_from_file_full(valid_file_path, full_dict_entry):
    write_object_to_file(valid_file_path, full_dict_entry)
    ret = read_object_from_file(valid_file_path)
    assert ret == full_dict_entry


def test_read_object_from_file_empty(valid_file_path, empty_dict_entry):
    write_object_to_file(valid_file_path, empty_dict_entry)
    ret = read_object_from_file(valid_file_path)
    assert ret == empty_dict_entry


def test_read_object_from_file_with_missing_file(invalid_missing_file_path, full_dict_entry):
    with pytest.raises(FileNotFoundError):
        read_object_from_file(invalid_missing_file_path)


def test_override_file_with_empty_info(valid_file_path, empty_dict_entry, full_dict_entry):
    write_object_to_file(valid_file_path, full_dict_entry)
    ret = read_object_from_file(valid_file_path)
    assert ret == full_dict_entry

    write_object_to_file(valid_file_path, empty_dict_entry)
    ret = read_object_from_file(valid_file_path)
    assert ret == empty_dict_entry
