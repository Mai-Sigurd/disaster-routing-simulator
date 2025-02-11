import json
from pathlib import Path

import geopandas as gpd
import pytest
import shapely

from data_loader.danger_zones import load_danger_zone


def test_load_danger_zone(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test loading a danger zone from a temporary GeoJSON file.
    Ensures that load_danger_zone works even though it looks in DATA_DIR.
    """

    coordinates = [
        (12.5, 55.5),
        (12.6, 55.6),
        (12.7, 55.7),
        (12.5, 55.5),
    ]
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[lon, lat] for lon, lat in coordinates]],
                },
            }
        ],
    }

    file_path = tmp_path / "danger_zones" / "test.geojson"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data))

    monkeypatch.setattr(
        "data_loader.danger_zones.DANGER_ZONES_DIR", tmp_path / "danger_zones"
    )

    danger_zone = load_danger_zone("test.geojson")
    assert isinstance(danger_zone, gpd.GeoDataFrame)
    assert len(danger_zone) == 1

    polygon = danger_zone.geometry[0]
    assert isinstance(polygon, shapely.Polygon)
    assert list(zip(*polygon.exterior.coords.xy)) == coordinates
