import geopandas as gpd
import networkx as nx
import pytest
from shapely.geometry import Polygon

from routes.shortestpath import route_to_safety

# Create a directed graph
G = nx.MultiDiGraph()

# Add nodes (coordinates as strings for simplicity)
G.add_node("A", x=2, y=2)
G.add_node("B", x=3, y=2)
G.add_node("C", x=3, y=3)
G.add_node("D", x=5, y=5)
G.add_node("E", x=4, y=4)

# Add edges with weights
G.add_edge("A", "B", length=1)
G.add_edge("B", "C", length=1)
G.add_edge("C", "D", length=2)
G.add_edge("C", "E", length=1)
G.add_edge("E", "D", length=2)

# Define a danger zone polygon
danger_zone = gpd.GeoDataFrame(geometry=[Polygon([(1, 4), (1, 1), (4, 1), (4, 4)])])

# List of origin points
origin_points = ["A"]


def test_route_to_safety() -> None:
    routes = route_to_safety(["A"], danger_zone, G)
    assert routes == [["A", "B", "C", "D"]]


def test_route_to_safety_more_than_one() -> None:
    routes = route_to_safety(["A", "B"], danger_zone, G)
    assert routes == [["A", "B", "C", "D"], ["B", "C", "D"]]


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
    routes = route_to_safety(["A"], danger_zone, G1)
    assert routes == [["A", "B", "C"]]


# Create a directed graph
G2 = nx.MultiDiGraph()

# Add nodes (coordinates as strings for simplicity)
G2.add_node("A", x=2, y=2)
G2.add_node("B", x=3, y=2)

# Add edges with weights
G2.add_edge("A", "B", length=1)


def test_route_to_safety_all_nodes_are_in_dangerzone() -> None:
    with pytest.raises(
        Exception, match="There are no reachable nodes outside the dangerzone"
    ):
        route_to_safety(["A"], danger_zone, G2)
