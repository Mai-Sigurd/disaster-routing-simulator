import logging

import osmnx as ox

from data_loader.danger_zones import load_danger_zone
from data_loader.osm import download_osm_graph
from matsim_io import write_network, write_plan

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{levelname}] {message}",
    style="{",
)


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
    danger_zones = load_danger_zone("dangerzone_amager.geojson")

    write_network(G, network_name="Copenhagen")
    write_plan(G)
