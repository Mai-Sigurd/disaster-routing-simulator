import gzip
import logging
import os
import shutil

import igraph
import sumolib
from routing_lib import from_sumo_to_igraph_network

from data_loader import DATA_DIR

OSM_DIR = DATA_DIR / "osm_graph"


def read_sumo_graph_as_polaris_igraph(filename: str) -> igraph.Graph:
    """
    Reads a SUMO graph from a gzipped XML file and converts it to an igraph format.
    :param filename: Name of the gzipped XML file containing the SUMO graph.
    :return: igraph.Graph object representing the road network.
    """
    if not filename.endswith(".gz"):
        raise ValueError(f"Invalid file name for SUMO graph: {filename}")
    filepath = OSM_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"SUMO graph file not found: {filepath}")

    logging.info(f"Loading SUMO graph: {filename}")
    decompressed_filepath = OSM_DIR / filename.rstrip(".gz")
    with gzip.open(filepath, "rb") as f_in, open(decompressed_filepath, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    road_network = sumolib.net.readNet(decompressed_filepath)
    os.remove(decompressed_filepath)

    logging.info("Converting SUMO graph to igraph format")
    polaris_graph = from_sumo_to_igraph_network(road_network)

    logging.info(f"Loaded SUMO graph: {filename}")
    return polaris_graph
