import networkx as nx
import osmnx as ox
import pytest

from data_loader.osm import download_osm_graph


@pytest.fixture
def mock_osm_graph() -> nx.MultiDiGraph:
    """Creates a fake OSM graph for testing."""
    graph = nx.MultiDiGraph()
    # A <-> B
    graph.add_edge("A", "B", length=100)
    graph.add_edge("B", "A", length=100)
    # B <-> C
    graph.add_edge("B", "C", length=200)
    graph.add_edge("C", "B", length=200)
    # C -> A
    graph.add_edge("C", "A", length=300)
    return graph


def test_download_osm_graph(
    monkeypatch: pytest.MonkeyPatch, mock_osm_graph: nx.MultiDiGraph
) -> None:
    """Test download_osm_graph without making actual API requests."""

    def mock_graph_from_place(
        query: str, network_type: str, simplify: bool
    ) -> nx.MultiDiGraph:
        """Mock function that replaces osmnx.graph_from_place."""
        return mock_osm_graph

    monkeypatch.setattr(ox, "graph_from_place", mock_graph_from_place)

    result_graph = download_osm_graph(["Fake City"])
    assert isinstance(result_graph, nx.MultiDiGraph)
    assert len(result_graph.edges) == len(mock_osm_graph.edges)
