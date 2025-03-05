import networkx as nx
import osmnx as ox
import pytest

from data_loader.osm import download_osm_graph


def test_download_osm_graph(
    monkeypatch: pytest.MonkeyPatch, mock_osm_graph: nx.MultiDiGraph
) -> None:
    """Test download_osm_graph without making actual API requests."""

    def mock_graph_from_bbox(
        bbox: tuple[float, float, float, float],
        network_type: str,
        simplify: bool,
        truncate_by_edge: bool,
    ) -> nx.MultiDiGraph:
        """Mock function that replaces osmnx.graph_from_place."""
        return mock_osm_graph

    monkeypatch.setattr(ox, "graph_from_bbox", mock_graph_from_bbox)

    result_graph = download_osm_graph(bbox=(0, 0, 1, 1))
    assert isinstance(result_graph, nx.MultiDiGraph)
    assert len(result_graph.edges) == len(mock_osm_graph.edges)
