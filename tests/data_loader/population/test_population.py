import logging
import sys
from unittest.mock import MagicMock, patch

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
import pytest
from _pytest.logging import LogCaptureFixture
from shapely.geometry import LineString, Point, Polygon

from data_loader.population import (
    POPULATION_DIR,
    distribute_population,
    get_total_population,
    population_data_from_geojson,
    population_data_from_number,
)
from data_loader.population.population_utils import (
    filter_world_pop_to_graph_area,
    snap_population_to_nodes,
)


@patch("geopandas.read_file")
def test_load_geojson_success(mock_read_file) -> None:  # type: ignore
    """Test successful loading of a GeoJSON file."""
    mock_gdf = MagicMock(spec=gpd.GeoDataFrame)
    mock_read_file.return_value = mock_gdf

    file_name = "test.geojson"
    result = population_data_from_geojson(file_name)

    mock_read_file.assert_called_once_with(POPULATION_DIR / file_name)
    assert result == mock_gdf


def test_load_geojson_failure(caplog: LogCaptureFixture) -> None:
    with patch("geopandas.read_file", side_effect=Exception("File not found")):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(SystemExit):  # Since the function calls exit(0)
                population_data_from_geojson("invalid_path.geojson")
        assert "Error loading GeoJSON file: File not found" in caplog.text


def test_distribute_population() -> None:
    # Create a mock danger zone (polygon)
    danger_zone = gpd.GeoDataFrame(
        {"id": [1]},
        geometry=[Polygon([(0, 0), (0, 10), (10, 10), (10, 0)])],
        crs="EPSG:4326",
    )

    # Create a mock population dataset (points)
    population = gpd.GeoDataFrame(
        {"pop": [100, 200, 50, 20, 300]},
        geometry=[
            Point(5, 5),
            Point(15, 15),
            Point(3, 3),
            Point(0, 0),
            Point(11, 11),
        ],  # 5,5 and 3,3 are definitely inside, 15,15 is outside, 0,0 is on the edge
        crs="EPSG:4326",
    )

    # Run function
    result = distribute_population(danger_zone, population)

    # Assertions
    assert isinstance(result, gpd.GeoDataFrame)
    assert (
        len(result) == 3
    )  # Only (5,5) and (3,3) are inside the polygon, 0,0 is on the edge also counted because we use intersect in sjoin
    assert "pop" in result.columns  # Population column should exist
    assert all(
        danger_zone.geometry.iloc[0].contains(pt)
        or danger_zone.geometry.iloc[0].touches(pt)
        for pt in result.geometry
    )


def test_population_data_from_number(
    monkeypatch: pytest.MonkeyPatch, mock_osm_graph: nx.MultiDiGraph
) -> None:
    # Create a mock danger zone (polygon)
    danger_zone = gpd.GeoDataFrame(
        {"id": [1]},
        geometry=[Polygon([(0, 0), (0, 60), (60, 60), (60, 0)])],
        crs="EPSG:4326",
    )
    # Create a mock population dataset (points)
    population = 500

    # Run function
    result = population_data_from_number(
        danger_zone=danger_zone, population_number=population, G=mock_osm_graph
    )
    # Assertions
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 5
    assert "pop" in result.columns  # Population column should exist
    # assert the population is evenly distributed
    assert all(result["pop"] == 100)


def test_filter_world_pop_to_cph() -> None:
    # Create a mock graph with nodes
    x = [0, 0, 10, 10]
    y = [0, 10, 0, 10]
    osmid = [1, 2, 3, 4]
    geometry = [Point(x, y) for x, y in zip(x, y)]
    graph_attrs = {"crs": "EPSG:4326"}
    gdf_nodes = gpd.GeoDataFrame(
        {"osmid": osmid, "x": x, "y": y, "geometry": geometry}, crs=graph_attrs["crs"]
    )
    edges_data = {
        "osmid": [1, 2],
        "geometry": [
            LineString([(0, 0), (10, 0)]),  # Edge 1: Line from (0, 0) to (10, 0)
            LineString([(10, 0), (10, 10)]),  # Edge 2: Line from (10, 0) to (10, 10)
        ],
    }

    # Create a MultiIndex for edges (u, v, key)
    multi_index = pd.MultiIndex.from_tuples(
        [(0, 1, 0), (1, 2, 0)], names=["u", "v", "key"]
    )

    # Create the edges GeoDataFrame with the multi-level index
    gdf_edges = gpd.GeoDataFrame(edges_data, index=multi_index, crs="EPSG:4326")
    G = ox.graph_from_gdfs(
        gdf_nodes=gdf_nodes, gdf_edges=gdf_edges, graph_attrs=graph_attrs
    )
    # Create a test GeoDataFrame with points
    test_df = gpd.GeoDataFrame(
        {"id": [1, 2, 3, 4]},
        geometry=[
            Point(5, 5),  # Inside
            Point(15, 15),  # Outside
            Point(0, 0),  # On edge (excluded)
            Point(10, 10),  # On edge (excluded)
        ],
    )

    # Run function
    result = filter_world_pop_to_graph_area(test_df, G)

    # Assertions
    assert isinstance(result, gpd.GeoDataFrame)
    print(result)
    assert len(result) == 1  # Only (5,5) should remain
    assert result.iloc[0].geometry == Point(5, 5)


# Import the function to test


def test_snap_population_to_nodes() -> None:
    x = [0, 0, 10, 10, 5, 10, 0, 5, 5]
    y = [0, 10, 0, 10, 10, 5, 5, 0, 5]
    osmid = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    geometry = [Point(x, y) for x, y in zip(x, y)]
    graph_attrs = {"crs": "EPSG:4326"}
    gdf_nodes = gpd.GeoDataFrame(
        {"osmid": osmid, "x": x, "y": y, "geometry": geometry}, crs=graph_attrs["crs"]
    )
    edges_data = {
        "osmid": [1, 2],
        "geometry": [
            LineString([(0, 0), (10, 0)]),  # Edge 1: Line from (0, 0) to (10, 0)
            LineString([(10, 0), (10, 10)]),  # Edge 2: Line from (10, 0) to (10, 10)
        ],
    }

    # Create a MultiIndex for edges (u, v, key)
    multi_index = pd.MultiIndex.from_tuples(
        [(0, 1, 0), (1, 2, 0)], names=["u", "v", "key"]
    )

    # Create the edges GeoDataFrame with the multi-level index
    gdf_edges = gpd.GeoDataFrame(edges_data, index=multi_index, crs="EPSG:4326")
    G = ox.graph_from_gdfs(
        gdf_nodes=gdf_nodes, gdf_edges=gdf_edges, graph_attrs=graph_attrs
    )
    # Create the population GeoDataFrame `df`
    population_data = {
        "id": [1, 2, 3],
        "geometry": [Point(5, 6), Point(11, 11), Point(8, 8)],  # Points near nodes
        "data": [100, 200, 300],  # Population data at these points
    }

    df = gpd.GeoDataFrame(population_data, crs="EPSG:4326")

    # Define maximum distance for snapping (in meters. however, the coordinate system here gets fucked when mapped to OSM)
    maximum_distance_to_node = sys.maxsize

    # Run the function
    result = snap_population_to_nodes(df, G, maximum_distance_to_node)

    # Assertions

    assert isinstance(result, gpd.GeoDataFrame)  # The result should be a GeoDataFrame
    assert len(result) == 2  # Expecting 2 points to be snapped to

    assert (
        result.iloc[0]["pop"] == 100
    )  # Population at the first node (Point(5,6) -> Node at location (5.5))
    assert (
        result.iloc[1]["pop"] == 500
    )  # Population at the second node (Point(8,8) and (11,11) -> Node 3; 200+300)

    # Assert the geometry at the nodes (the geometry should match the nodes' geometry)
    assert result.iloc[0]["geometry"] == geometry[8]
    assert result.iloc[1]["geometry"] == geometry[3]


def test__get_total_population() -> None:
    population_data = gpd.GeoDataFrame(data={"pop": [10, 20]})
    result = get_total_population(population_data, 1.0)
    assert result == 30
