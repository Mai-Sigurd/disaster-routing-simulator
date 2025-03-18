import logging

import geopandas as gpd
import networkx as nx
import pytest
from _pytest.logging import LogCaptureFixture
from shapely.geometry import Polygon

from routes.polaris import Weight, polaris_paths

# Create a directed graph
G = nx.MultiDiGraph()

# Add nodes
G.add_node("A", x=2, y=2)
G.add_node("B", x=3, y=2)
G.add_node("C", x=3, y=3)
G.add_node("D", x=5, y=5)
G.add_node("E", x=4, y=4)

# Add edges with weights
G.add_edge("A", "B", length=1, maxspeed=50)
G.add_edge("B", "C", length=1, maxspeed=50)
G.add_edge("C", "D", length=2, maxspeed=50)
G.add_edge("C", "E", length=1, maxspeed=50)
G.add_edge("E", "D", length=2, maxspeed=50)

# Define a danger zone polygon
danger_zone = gpd.GeoDataFrame(geometry=[Polygon([(1, 4), (1, 1), (4, 1), (4, 4)])])

# List of origin, dest points
origin_dest_pairs = [("A", "D"), ("A", "C"), ("B", "E")]


def test_polaris_with_weight_length() -> None:
    routes = polaris_paths(origin_dest_pairs, G, Weight.LENGTH)
    assert routes == [["A", "B", "C", "D"]]
