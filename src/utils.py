from pathlib import Path

DISASTER_DIR = Path(__file__).resolve().parent.parent


def kmh_to_ms(kmh: float) -> float:
    """Convert km/h to m/s."""
    return kmh * 1000 / 3600

