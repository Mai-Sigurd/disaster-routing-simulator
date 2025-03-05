import logging

import networkx as nx
import osmnx as ox

from data_loader import DATA_DIR

COPENHAGEN_BBOX = (12.42, 55.55, 12.81, 55.76)
OSM_DIR = DATA_DIR / "osm_graph"


def download_osm_graph(
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
    logging.info(
        f"Loaded OSM graph {len(graph.nodes)} nodes and {len(graph.edges)} edges from {filename}"
    )
    return graph
