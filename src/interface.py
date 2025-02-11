import heapq as hq
from typing import Dict, List, Tuple

import geopandas as gpd
import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import Point

vertex = str
"""A tuple containing the latitude and longitude of a point"""

route = list[vertex]
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
) -> list[tuple[Point, int]]:
    """
    Distributes the population of a danger zone across the surrounding areas.
    :return: A list of tuples where each tuple contains a coordinate and the number of people at that coordinate.
    """
    raise NotImplementedError


# based on: https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/
def route_to_safety(
    origin_points: list[vertex], danger_zone: gpd.GeoDataFrame, G: nx.MultiDiGraph
) -> list[route]:
    """
    Routes a list of origin points to the nearest safe location.

    :param origin_points: A list of buckets, where each bucket contains road segments with a number of cars.
    :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
    :return: A list of routes where each route corresponds to the origin points at the same index.
    """
    routes = []

    for origin in origin_points:
        sptSet = dict((node, False) for node in list(G.nodes))
        dist: list[tuple[float, str]] = [(float("inf"), node) for node in G.nodes]
        node_priority = {node: float("inf") for node in G.nodes}
        hq.heapify(dist)
        predecessor: dict[str, str | None] = {
            node: None for node in G.nodes
        }  # To track shortest path

        nearestNode = nx.distance.nearest_nodes(G, origin[0], origin[1])
        update_priority(dist, node_priority, nearestNode, 0)

        while not all(
            sptSet.values()
        ):  # while there are still elements in sptSet that are false
            priority, smallest_node = dist[0]
            if (
                priority == node_priority[smallest_node]
            ):  # Only use values that are not outdated
                if not sptSet[smallest_node]:
                    sptSet[smallest_node] = True
                    for neighbour in G.successors[smallest_node]:
                        for _, _, edge_data in G.edges(
                            smallest_node, neighbour, data=True
                        ):  # Multiple edges between two nodes possible
                            weight = edge_data.get(
                                "weight", float("inf")
                            )  # Default weight to inf, weight of edge between popped_node and neighbour
                            new_distance = priority + weight

                            if new_distance < node_priority[neighbour]:
                                update_priority(
                                    dist, node_priority, neighbour, new_distance
                                )
                                predecessor[neighbour] = smallest_node

            if not is_in_dangerzone(
                smallest_node, danger_zone
            ):  # We have found shortest route to node outside dangerzone
                routes.append(reconstruct_route(predecessor, smallest_node))
                break  # there is no need to find other routes

    return routes


def reconstruct_route(predecessor: Dict[str, str | None], end: str) -> List[str]:
    path = []
    while end is not None:
        path.append(end)
        end = predecessor[end]  # type: ignore
    return path[::-1]


def is_in_dangerzone(v: vertex, danger_zone: gpd.GeoDataFrame) -> bool:
    p = gpd.GeoSeries(
        [
            Point(v[0], v[1]),
        ],
    )
    return danger_zone.intersects(p)[0]  # type: ignore


def update_priority(
    heap: List[Tuple[float, str]],
    node_priority: Dict[str, float],
    node: str,
    new_priority: float,
) -> None:
    if new_priority < node_priority[node]:  # Only update if the new priority is better
        hq.heappush(heap, (new_priority, node))  # Push the new priority
        node_priority[node] = new_priority


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
