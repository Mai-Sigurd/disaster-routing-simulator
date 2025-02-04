import logging

import networkx as nx
import osmnx as ox

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)


def download_osm_graph(queries: list[str]) -> nx.MultiDiGraph:
    def download_query(query: str) -> nx.MultiDiGraph:
        logging.info(f"Downloading graph for {query}")
        city_graph = ox.graph_from_place(
            query, network_type="drive_service", simplify=True
        )
        logging.info(f"Downloaded graph for {query}")
        return city_graph

    return nx.compose_all([download_query(city) for city in queries])


if __name__ == "__main__":
    # G = download_osm_graph(["Capital Region of Denmark"])
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
    fig, ax = ox.plot.plot_graph(G, node_size=0, edge_linewidth=0.5, figsize=(10, 10))
