import logging

import geopandas as gpd
import networkx as nx
from _pytest.logging import LogCaptureFixture
from shapely.geometry import Polygon

from routes.fastestpath import fastest_path

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

# List of origin points
origin_points = ["A"]


def test_fastest_path() -> None:
    routes = fastest_path(["A"], danger_zone, G)
    assert routes == [["A", "B", "C", "D"]]


def test_fastest_path_two_origin_points() -> None:
    routes = fastest_path(["A", "B"], danger_zone, G)
    assert routes == [["A", "B", "C", "D"], ["B", "C", "D"]]


def test_fastest_path_three_origin_points() -> None:
    routes = fastest_path(["A", "B", "C"], danger_zone, G)
    assert routes == [["A", "B", "C", "D"], ["B", "C", "D"], ["C", "D"]]


# Create a directed graph
G1 = nx.MultiDiGraph()

# Add nodes
G1.add_node("A", x=2, y=2)
G1.add_node("B", x=3, y=3)
G1.add_node("C", x=5, y=5)

# Add edges with weights
G1.add_edge("A", "B", length=1, maxspeed=110)
G1.add_edge("B", "C", length=1, maxspeed=110)
G1.add_edge("A", "C", length=2, maxspeed=50)


def test_fastest_path_takes_fastest_route() -> None:
    routes = fastest_path(["A"], danger_zone, G1)
    assert routes == [["A", "B", "C"]]


# Create a directed graph
G2 = nx.MultiDiGraph()

# Add nodes
G2.add_node("A", x=2, y=2)
G2.add_node("B", x=6, y=6)
G2.add_node("C", x=5, y=5)

# Add edges with weights
G2.add_edge("A", "B", length=5, maxspeed=100)
G2.add_edge("A", "C", length=5, maxspeed=99)


def test_fastest_path_takes_fastest_route2() -> None:
    routes = fastest_path(["A"], danger_zone, G2)
    assert routes == [["A", "B"]]


# Create a directed graph
G3 = nx.MultiDiGraph()

# Add nodes (coordinates as strings for simplicity)
G3.add_node("A", x=2, y=2)
G3.add_node("B", x=3, y=2)

# Add edges with weights
G3.add_edge("A", "B", length=1, maxspeed=50)


def test_fastest_path_all_nodes_are_in_dangerzone_logging(
    caplog: LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        fastest_path(["A"], danger_zone, G3)
    assert "Node A cannot reach any nodes outside the dangerzone" in caplog.text


# Create a directed graph
G4 = nx.MultiDiGraph()

# Add nodes (coordinates as strings for simplicity)
G4.add_node("A", x=2, y=2)
G4.add_node("B", x=3, y=2)
G4.add_node("C", x=4, y=2)

# Add edges with weights
G4.add_edge("B", "C", length=1, maxspeed=222)


def test_fastest_path_origin_has_no_neighbours_logging(
    caplog: LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        fastest_path(["A"], danger_zone, G4)
    assert "Node A has no neighbors" in caplog.text
