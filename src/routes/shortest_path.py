from typing import Dict

import geopandas as gpd
import networkx as nx
import zope.interface

from routes.route_algo import RouteAlgo
from routes.route_utils import path, route_to_safety_with_weight_func, vertex


@zope.interface.implementer(RouteAlgo)
class ShortestPath:
    def __init__(self) -> None:
        self.title = "Dijkstra - Shortest Path"

    # based on: https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/
    def route_to_safety(
        self,
        origin_points: list[vertex],
        danger_zone: gpd.GeoDataFrame,
        G: nx.MultiDiGraph,
        diversifying_routes: int = 1,
    ) -> Dict[vertex, list[path]]:
        """
        Routes a list of origin points to the nearest safe location.

        :param origin_points: A list of vertices given as str IDs
        :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
        :param G: A graph corresponding to the road network
        :param diversifying_routes: The number of routes to find for each origin point
        :return: A dictionary from an origin point to a list of 1 or more paths
        """
        routes: Dict[vertex, list[path]] = route_to_safety_with_weight_func(
            origin_points=origin_points,
            danger_zone=danger_zone,
            G=G,
            weight_func=_shortest_path_weight_func,
            diversifying_routes=diversifying_routes,
        )
        return routes


def _shortest_path_weight_func(priority: float, edge_data) -> float:  # type: ignore
    """
    Calculates the weight of an edge in the shortest path algorithm.
    :param priority: The current priority of the node.
    :param edge_data: The data associated with the edge.
    """
    weight = edge_data.get("length", float("inf"))
    # Default weight to inf, weight of edge between smallest_node and neighbour
    new_distance: float = priority + weight
    return new_distance
