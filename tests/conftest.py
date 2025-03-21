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
    graph.add_edge("A", "B", length=100, maxspeed=50, lanes=1, oneway=False)
    graph.add_edge("B", "A", length=100, maxspeed=50, lanes=1, oneway=False)
    graph.add_edge("B", "C", length=200, maxspeed=50, lanes=1, oneway=False)
    graph.add_edge("C", "B", length=200, maxspeed=50, lanes=1, oneway=False)

    # A <- C -> D -> E
    graph.add_edge("C", "A", length=300, maxspeed=80, lanes=2, oneway=True)
    graph.add_edge("C", "D", length=400, maxspeed=130, lanes=3, oneway=True)
    graph.add_edge("D", "E", length=150, maxspeed=50, lanes=1, oneway=True)

    return graph


@pytest.fixture
def mock_routes() -> list[Route]:
    """Creates a list of fake routes for testing."""
    return [
        Route(["A", "B", "C", "D", "E"], 20, [0] * 20),
        Route(["B", "C", "A"], 10, [0] * 10),
    ]


@pytest.fixture
def osm_graph_bbox() -> str:
    return """{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"coordinates":[[[12.81,55.55],[12.81,55.76],[12.45,55.76],[12.45,55.55],[12.81,55.55]]],"type":"Polygon"}}]}"""


@pytest.fixture
def danger_zone() -> str:
    return """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              12.594123364652546,
              55.66912772371745
            ],
            [
              12.584146557259686,
              55.66456970063598
            ],
            [
              12.583388792512977,
              55.65958322991645
            ],
            [
              12.603720195262099,
              55.6530278384474
            ],
            [
              12.616980393896057,
              55.65979627384672
            ],
            [
              12.614835102218962,
              55.67090934974513
            ],
            [
              12.605110429625654,
              55.672902898841926
            ],
            [
              12.594123364652546,
              55.66912772371745
            ]
          ]
        ],
        "type": "Polygon"
      }
    }
  ]
}"""
