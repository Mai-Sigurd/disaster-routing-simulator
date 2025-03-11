import logging

import networkx as nx
import osmnx as ox
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon

from data_loader import DATA_DIR, load_json

COPENHAGEN_BBOX = (12.42, 55.55, 12.81, 55.76)
OSM_DIR = DATA_DIR / "osm_graph"


def download_osm_graph(bbox_file_name: str, simplify: bool = True) -> nx.MultiDiGraph:
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
    data = load_json(filepath)
    logging.info(f"Loaded bounding box: {bbox_file_name}")

    polygon = shape(data["features"][0]["geometry"])
    if not isinstance(polygon, Polygon):
        raise ValueError("Bounding box must be a single Polygon.")

    coords = list(polygon.exterior.coords)
    if len(coords) != 5 or coords[0] != coords[-1]:
        raise ValueError(
            "Bounding box polygon must have exactly 5 coordinates, forming a closed shape."
        )

    left, bottom, right, top = polygon.bounds
    logging.info(f"Extracted bounding box: ({left}, {bottom}, {right}, {top})")

    return download_graph_from_bbox((left, bottom, right, top), simplify)


def download_graph_from_bbox(
    bbox: tuple[float, float, float, float], simplify: bool = True
) -> nx.MultiDiGraph:
    """
    Download an OSM graph from a bounding box.
    :param bbox: Bounding box of the area to download, formatted (left, bottom, right, top).
    :param simplify: Whether to simplify the graph.
    :return: OSM graph containing the road network in the bounding box.
    """
    logging.info("Downloading OSM graph")
    graph = ox.graph_from_bbox(
        bbox=bbox,
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
    return download_osm_graph("cph_bbox.geojson")


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
