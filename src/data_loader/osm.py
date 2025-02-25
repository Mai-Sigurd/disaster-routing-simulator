import logging

import networkx as nx
import osmnx as ox

from data_loader import DATA_DIR

COPENHAGEN_BBOX = (12.425, 55.550, 12.710, 55.755)
OSM_DIR = DATA_DIR / "osm_graph"


def download_osm_graph(bbox: tuple[float, float, float, float]) -> nx.MultiDiGraph:
    """
    Download an OSM graph from a bounding box.
    :param bbox: Bounding box of the area to download, formatted (left, bottom, right, top).
    :return: OSM graph containing the road network in the bounding box.
    """
    logging.info("Downloading OSM graph")
    city_graph = ox.graph_from_bbox(
        bbox=bbox,
        network_type="drive_service",
        retain_all=True,
    )
    logging.info("Downloaded OSM graph")
    return city_graph


def download_cph() -> nx.MultiDiGraph:
    """Download the OSM graph of Copenhagen."""
    return download_osm_graph(COPENHAGEN_BBOX)


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
    logging.info(f"Loaded OSM graph from {filename}")
    return graph
