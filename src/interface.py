import geopandas as gpd
import networkx as nx
import pandas as pd
import shapely

route = list[shapely.geometry.Point]
"""A list of coordinates representing a route"""


def download_osm_graph(queries: list[str]) -> nx.MultiDiGraph:
    """
    Downloads OpenStreetMap graphs for a list of queries and composes them into a single MultiDiGraph.
    """
    raise NotImplementedError


def load_danger_zone(file_name: str) -> gpd.GeoDataFrame:
    """
    Loads a danger zone GeoJSON file and returns a GeoDataFrame with the danger zone polygon(s).
    """
    raise NotImplementedError


def distribute_population(
    danger_zone: gpd.GeoDataFrame,
) -> list[tuple[shapely.geometry.Point, int]]:
    """
    Distributes the population of a danger zone across the surrounding areas.
    :return: A list of tuples where each tuple contains a coordinate and the number of people at that coordinate.
    """
    raise NotImplementedError


def route_to_safety(
    origin_points: list[shapely.geometry.Point], danger_zone: gpd.GeoDataFrame
) -> list[route]:
    """
    Routes a list of origin points to the nearest safe location.

    :param origin_points: A list of buckets, where each bucket contains road segments with a number of cars.
    :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
    :return: A list of routes where each route corresponds to the origin points at the same index.
    """
    raise NotImplementedError


def simulate_routes(
    routes: list[route],
    time_step: float = 1.0,
) -> list[pd.DataFrame]:
    """
    Simulates the movement of cars along a list of routes.
    The simulation should be dependent on the road speeds and lengths.

    :param routes: A list of routes where each route is a list of coordinates.
    :param time_step: The time step for the simulation in seconds.
    :return: A list of DataFrames containing the simulation results with columns ['time', 'latitude', 'longitude'].
    """
    raise NotImplementedError


def introduce_departure_time(
    simulated_routes: list[pd.DataFrame],
    departure_times: any,  # type: ignore
) -> list[pd.DataFrame]:
    """
    Splits the simulated routes into multiple DataFrames based on the departure times of the cars.

    :param simulated_routes: A list of DataFrames containing the simulation results.
    :param departure_times: A way to describe the departure times of the cars.
    :return: A list of DataFrames where each DataFrame contains the simulation results for a specific departure time.
    """
    raise NotImplementedError


def write_to_kepler(simulated_routes: list[pd.DataFrame]) -> None:
    """
    Write the simulation results to a format that can be visualized in Kepler.gl.
    """
    raise NotImplementedError
