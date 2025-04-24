import logging

import geopandas as gpd
import networkx as nx
from _pytest.logging import LogCaptureFixture
from shapely.geometry import Polygon

from routes.shortest_path import ShortestPath

# Create a directed graph
G = nx.MultiDiGraph()

# Add nodes (coordinates as strings for simplicity)
G.add_node("A", x=2, y=2)
G.add_node("B", x=3, y=2)
G.add_node("B1", x=2, y=3)
G.add_node("C", x=3, y=3)
G.add_node("D", x=5, y=5)
G.add_node("E", x=4, y=4)
G.add_node("F", x=6, y=6)
G.add_node("G", x=7, y=7)

# Add edges with weights
G.add_edge("A", "B", length=1)
G.add_edge("A", "B1", length=1)
G.add_edge("B", "C", length=1)
G.add_edge("C", "D", length=2)
G.add_edge("C", "E", length=1)
G.add_edge("E", "D", length=2)
G.add_edge("B", "F", length=10)
G.add_edge("B1", "G", length=7)

# Define a danger zone polygon
danger_zone = gpd.GeoDataFrame(geometry=[Polygon([(1, 4), (1, 1), (4, 1), (4, 4)])])

# List of origin points
origin_points = ["A"]
sp = ShortestPath()


def test_route_to_safety() -> None:
    routes = sp.route_to_safety(["A"], danger_zone, G)
    assert (["A", "B", "C", "D"]) in routes["A"]
    assert (["A", "B", "F"]) in routes["A"]
    assert (["A", "B1", "G"]) in routes["A"]
    assert len(routes["A"]) == 3


def test_route_to_safety_two_origin_points() -> None:
    routes = sp.route_to_safety(["A", "B"], danger_zone, G)
    assert (["A", "B", "C", "D"]) in routes["A"]
    assert (["A", "B", "F"]) in routes["A"]
    assert (["A", "B1", "G"]) in routes["A"]
    assert (["B", "C", "D"]) in routes["B"]
    assert (["B", "F"]) in routes["B"]
    assert len(routes["A"]) == 3
    assert len(routes["B"]) == 2


def test_route_to_safety_three_origin_points() -> None:
    routes = sp.route_to_safety(["A", "B", "C"], danger_zone, G)
    assert (["A", "B", "C", "D"]) in routes["A"]
    assert (["A", "B", "F"]) in routes["A"]
    assert (["A", "B1", "G"]) in routes["A"]
    assert (["B", "C", "D"]) in routes["B"]
    assert (["B", "F"]) in routes["B"]
    assert (["C", "D"]) in routes["C"]
    assert len(routes["A"]) == 3
    assert len(routes["B"]) == 2
    assert len(routes["C"]) == 1


# Create a directed graph
G1 = nx.MultiDiGraph()

# Add nodes (coordinates as strings for simplicity)
G1.add_node("A", x=2, y=2)
G1.add_node("B", x=4, y=4)
G1.add_node("C", x=5, y=5)

# Add edges with weights
G1.add_edge("A", "B", length=1)
G1.add_edge("B", "C", length=1)


def test_route_to_safety_endpoint_is_completely_free_from_danger() -> None:
    routes = sp.route_to_safety(["A"], danger_zone, G1, 1)
    assert routes["A"] == [["A", "B", "C"]]


# Create a directed graph
G2 = nx.MultiDiGraph()

# Add nodes (coordinates as strings for simplicity)
G2.add_node("A", x=2, y=2)
G2.add_node("B", x=3, y=2)

# Add edges with weights
G2.add_edge("A", "B", length=1)


def test_route_to_safety_all_nodes_are_in_dangerzone_logging(
    caplog: LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        sp.route_to_safety(["A"], danger_zone, G2, 1)
    assert "Node A cannot reach any nodes outside the dangerzone" in caplog.text


# Create a directed graph
G3 = nx.MultiDiGraph()

# Add nodes (coordinates as strings for simplicity)
G3.add_node("A", x=2, y=2)
G3.add_node("B", x=3, y=2)
G3.add_node("C", x=4, y=2)

# Add edges with weights
G3.add_edge("B", "C", length=1)


def test_route_to_safety_origin_has_no_neighbours_logging(
    caplog: LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO):
        sp.route_to_safety(["A"], danger_zone, G3, 1)
    assert "Node A has no neighbors" in caplog.text
