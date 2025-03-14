import json
import logging
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DANGER_ZONES_DIR = DATA_DIR / "danger_zones"

def load_json_file(file_path: Path) -> dict:  # type: ignore
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

def load_json_file_to_str(file_name: str) -> str:
    """
    Loads a GeoJSON file from a given path.

    :param file_name: Name of the GeoJSON file stored in DANGER_ZONES_DIR
    :return: Parsed GeoJSON dictionary
    """
    file_path = DANGER_ZONES_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {file_path}")

    logging.info(f"Loading JSON file: {file_path}")
    with open(file_path, "r") as f:
        return f.read()