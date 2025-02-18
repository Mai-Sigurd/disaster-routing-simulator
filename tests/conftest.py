import networkx as nx
import pytest

from routes.route import Route


@pytest.fixture
def mock_osm_graph() -> nx.MultiDiGraph:
    """Creates a fake OSM graph for testing with node coordinates."""
    graph = nx.MultiDiGraph()

    graph.add_node("A", x=12.5, y=55.5)
    graph.add_node("B", x=12.6, y=55.6)
    graph.add_node("C", x=12.7, y=55.7)
    graph.add_node("D", x=12.8, y=55.8)
    graph.add_node("E", x=12.9, y=55.9)

    # A <-> B <-> C
    graph.add_edge("A", "B", length=100, maxspeed=50, lanes=1)
    graph.add_edge("B", "A", length=100, maxspeed=50, lanes=1)
    graph.add_edge("B", "C", length=200, maxspeed=50, lanes=1)
    graph.add_edge("C", "B", length=200, maxspeed=50, lanes=1)

    # A <- C -> D -> E
    graph.add_edge("C", "A", length=300, maxspeed=80, lanes=2)
    graph.add_edge("C", "D", length=400, maxspeed=130, lanes=3)
    graph.add_edge("D", "E", length=150, maxspeed=50, lanes=1)

    return graph


@pytest.fixture
def mock_routes() -> list[Route]:
    """Creates a list of fake routes for testing."""
    return [
        Route(["A", "B", "C", "D", "E"], 20),
        Route(["B", "C", "A"], 10),
    ]
