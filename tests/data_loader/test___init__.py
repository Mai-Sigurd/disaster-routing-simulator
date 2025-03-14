import json
from pathlib import Path

import pytest

from data_loader import load_json_file


def test_load_json_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_json_file(tmp_path / "test.json")


def test_load_json_correct_loading(tmp_path: Path) -> None:
    data = {"key": "value"}
    file_path = tmp_path / "test.json"
    file_path.write_text(json.dumps(data))

    loaded_data = load_json_file(file_path)
    assert loaded_data == data
