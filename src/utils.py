import os
from pathlib import Path

DISASTER_DIR = Path(__file__).resolve().parent.parent


def kmh_to_ms(kmh: float) -> float:
    """Convert km/h to m/s."""
    return kmh * 1000 / 3600


def get_path_relative_to_disaster_dir(path: str) -> str:
    """Get the path relative to the disaster directory."""
    return os.path.join(DISASTER_DIR, path)
