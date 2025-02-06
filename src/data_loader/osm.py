import logging

import networkx as nx
import osmnx as ox


def download_osm_graph(queries: list[str]) -> nx.MultiDiGraph:
    def download_query(query: str) -> nx.MultiDiGraph:
        logging.info(f"Downloading graph for {query}")
        city_graph = ox.graph_from_place(
            query, network_type="drive_service", simplify=True
        )
        logging.info(f"Downloaded graph for {query}")
        return city_graph

    return nx.compose_all([download_query(city) for city in queries])
