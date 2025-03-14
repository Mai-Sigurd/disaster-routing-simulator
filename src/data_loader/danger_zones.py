import logging
import json
import geopandas as gpd
from shapely.geometry import shape

from data_loader import DATA_DIR, load_json_file

DANGER_ZONES_DIR = DATA_DIR / "danger_zones"


def load_danger_zone(file_name: str, crs: str) -> gpd.GeoDataFrame:
    """
    Loads a danger zone GeoJSON file and returns a GeoDataFrame.

    :param file_name: Name of the GeoJSON file (e.g., "dangerzone_1.geojson")
    :param crs: Coordinate Reference System
    :return: GeoDataFrame containing the danger zone polygon(s)
    """
    if not file_name.endswith(".geojson"):
        raise ValueError(f"Invalid file name: {file_name}")

    logging.info(f"Loading danger zone: {file_name}")
    filepath = DANGER_ZONES_DIR / file_name
    data = load_json_file(filepath)

    logging.info(f"Loaded danger zone: {file_name}")
    polygons = [shape(feature["geometry"]) for feature in data["features"]]
    return gpd.GeoDataFrame(geometry=polygons, crs=crs)


def load_danger_zone_from_str(geo_json: str, crs: str) -> gpd.GeoDataFrame:
    """
    Loads a danger zone GeoJSON string and returns a GeoDataFrame.

    :param geo_json: GeoJSON string
    :param crs: Coordinate Reference System
    :return: GeoDataFrame containing the danger zone polygon(s)
    """
    data = json.loads(geo_json)

    polygons = [shape(feature["geometry"]) for feature in data["features"]]
    return gpd.GeoDataFrame(geometry=polygons, crs=crs)


def set_danger_zone_crs(danger_zone: gpd.GeoDataFrame, crs: str) -> gpd.GeoDataFrame:
    if danger_zone.crs is None:
        danger_zone.set_crs(crs, inplace=True)

    return danger_zone.to_crs(crs, inplace=True)
