import json
import logging

import networkx as nx
import osmnx as ox
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon

from data_loader import DATA_DIR, load_json_file

OSM_DIR = DATA_DIR / "osm_graph"


def download_osm_graph_with_bbox_file(
    bbox_file_name: str, simplify: bool = True
) -> nx.MultiDiGraph:
    """
    Loads a GeoJSON file containing a single polygon with exactly 5 coordinates
    and extracts its bounding box.

    :param bbox_file_name: Name of the GeoJSON file (e.g., "bbox.geojson").
    :param simplify: Whether to simplify the graph.
    :return: OSM graph containing the road network in the bounding box.
    """
    if not bbox_file_name.endswith(".geojson"):
        raise ValueError(f"Invalid file name for bounding box: {bbox_file_name}")

    logging.info(f"Loading bounding box: {bbox_file_name}")
    filepath = DATA_DIR / "bbox" / bbox_file_name
    geo_json = load_json_file(filepath)
    bbox = _geojson_as_polygon(geo_json["features"][0]["geometry"])
    logging.info(f"Loaded bounding box: {bbox_file_name}")

    return download_osm_graph(bbox, simplify)


def download_osm_graph_with_bbox_string(
    geo_json: str, simplify: bool = True
) -> nx.MultiDiGraph:
    """
    Loads a GeoJSON string containing a single polygon with exactly 5 coordinates
    and extracts its bounding box.

    :param geo_json: GeoJSON string.
    :param simplify: Whether to simplify the graph.
    :return: OSM graph containing the road network in the bounding box.
    """
    bbox = geojson_str_to_polygon(geo_json)
    return download_osm_graph(bbox, simplify)


def download_osm_graph_from_polygon(geo_json: str) -> nx.MultiDiGraph:
    """
    Loads a GeoJSON string containing a single polygon with exactly 5 coordinates
    and extracts its bounding box.

    :param geo_json: GeoJSON string.
    :return: OSM graph containing the road network in the bounding box.
    """
    polygon = geojson_str_to_polygon(geo_json)
    return download_osm_graph(polygon)


def download_osm_graph(polygon: Polygon, simplify: bool = True) -> nx.MultiDiGraph:
    """
    Download the OSM graph within the given polygon.
    :param polygon: Polygon representing the area of interest.
    :param simplify: Whether to simplify the graph.
    :return: OSM graph containing the road network in the bounding box.
    """
    logging.info(f"Downloading OSM graph with bounding polygon: {polygon.bounds}")
    graph = ox.graph_from_polygon(
        polygon=polygon,
        network_type="drive_service",
        simplify=simplify,
        truncate_by_edge=True,
    )
    logging.info(
        f"Downloaded OSM graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges"
    )
    return graph


def download_cph() -> nx.MultiDiGraph:
    """Download the OSM graph of Copenhagen."""
    return download_osm_graph_with_bbox_file("cph_bbox.geojson")


def save_osm(graph: nx.MultiDiGraph, filename: str) -> None:
    """
    Save an OSM graph to a file in the OSM data directory.
    :param graph: OSM graph to save.
    :param filename: Name of the file to save the graph to.
    """
    logging.info(f"Saving OSM graph to {filename}")
    ox.save_graphml(graph, OSM_DIR / filename)
    logging.info(f"Saved OSM graph to {filename}")


def load_osm(filename: str) -> nx.MultiDiGraph:
    """
    Load an OSM graph from a file in the OSM data directory.
    :param filename: Name of the file to load the graph from.
    :return: OSM graph loaded from the file.
    """
    logging.info(f"Loading OSM graph from {filename}")
    graph = ox.load_graphml(OSM_DIR / filename)
    logging.info(
        f"Loaded OSM graph {len(graph.nodes)} nodes and {len(graph.edges)} edges from {filename}"
    )
    return graph


def geojson_str_to_polygon(geo_json: str) -> Polygon:
    """
    Loads a GeoJSON string containing a single polygon with exactly 5 coordinates
    and extracts its bounding box.

    :param geo_json: GeoJSON string.
    :return: Polygon containing the bounding box.
    """
    return _geojson_as_polygon(json.loads(geo_json))


def _geojson_as_polygon(data: dict) -> Polygon:  # type: ignore[type-arg]
    polygon = shape(data["features"][0]["geometry"])
    if not isinstance(polygon, Polygon):
        raise ValueError("Bounding box must be a single Polygon.")
    return polygon
