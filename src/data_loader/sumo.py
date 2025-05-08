import gzip
import logging
import os
import shutil

import sumolib

from data_loader import DATA_DIR

OSM_DIR = DATA_DIR / "osm_graph"


def read_sumo_road_network(filename: str) -> sumolib.net.Net:
    """
    Reads a SUMO road network from a gzipped XML file.
    :param filename: Name of the gzipped XML file containing the SUMO graph.
    :return: SUMO road network as a sumolib.net.Net object.
    """
    if not filename.endswith(".gz"):
        raise ValueError(f"Invalid file name for SUMO graph: {filename}")
    filepath = OSM_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"SUMO graph file not found: {filepath}")

    logging.info(f"Loading SUMO road network: {filename}")
    decompressed_filepath = OSM_DIR / filename.rstrip(".gz")
    with gzip.open(filepath, "rb") as f_in, open(decompressed_filepath, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    try:
        road_network = sumolib.net.readNet(decompressed_filepath)
    finally:
        os.remove(decompressed_filepath)

    logging.info("Loaded SUMO road network successfully")
    return road_network
