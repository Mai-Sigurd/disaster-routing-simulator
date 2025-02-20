import logging

import networkx as nx
import osmnx as ox

from data_loader import DATA_DIR

OSM_DIR = DATA_DIR / "osm_graph"


def download_osm_graph(queries: list[str]) -> nx.MultiDiGraph:
    def download_query(query: str) -> nx.MultiDiGraph:
        logging.info(f"Downloading graph for {query}")
        city_graph = ox.graph_from_place(
            query, network_type="drive_service", simplify=True
        )
        logging.info(f"Downloaded graph for {query}")
        return city_graph

    return nx.compose_all([download_query(city) for city in queries])


def download_cph() -> None:
    G = download_osm_graph(
        [
            "Copenhagen Municipality, Denmark",
            "Frederiksberg Municipality, Denmark",
            "Tårnby Municipality, Denmark",
            "Hvidovre Municipality, Denmark",
            "Rødovre Municipality, Denmark",
            "Gentofte Municipality, Denmark",
            "Gladsaxe Municipality, Denmark",
            "Herlev Municipality, Denmark",
        ]
    )
    save_osm(G, "copenhagen.graphml")


def save_osm(G: nx.MultiDiGraph, filename: str) -> None:
    ox.save_graphml(G, OSM_DIR / filename)


def load_osm(filename: str) -> nx.MultiDiGraph:
    return ox.load_graphml(OSM_DIR / filename)
