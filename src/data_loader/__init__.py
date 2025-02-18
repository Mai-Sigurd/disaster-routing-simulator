import json
import logging
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_json(file_path: Path) -> dict:  # type: ignore
    """
    Loads a GeoJSON file from a given path.

    :param file_path: Full path to the GeoJSON file
    :return: Parsed GeoJSON dictionary
    """
    if not file_path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {file_path}")

    logging.info(f"Loading JSON file: {file_path}")
    with open(file_path, "r") as f:
        return json.load(f)  # type: ignore
