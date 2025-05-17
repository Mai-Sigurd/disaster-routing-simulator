import logging
from typing import Dict

import geopandas as gpd
import networkx as nx
import zope.interface

from routes.route_algo import RouteAlgo
from routes.route_utils import path, route_to_safety_with_weight_func, vertex
from utils import kmh_to_ms


@zope.interface.implementer(RouteAlgo)
class FastestPath:
    def __init__(self) -> None:
        self.title = "Dijkstra - Fastest Path"

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
        :return: A list of routes where each route corresponds to the origin point at the same index.
        """

        logging.info("Routing fastest path to safety for all origin points")

        routes: Dict[vertex, list[path]] = route_to_safety_with_weight_func(
            origin_points=origin_points,
            danger_zone=danger_zone,
            G=G,
            weight_func=_fastest_path_weight_function,
            diversifying_routes=diversifying_routes,
        )
        return routes


def _fastest_path_weight_function(priority: float, edge_data) -> float:  # type:ignore
    length = edge_data.get(
        "length", float("inf")
    )  # Default weight to inf, weight of edge between smallest_node and neighbour

    max_speed = edge_data.get("maxspeed", 50)  # speed limit km/h, default 50
    max_speed = (
        max_speed[0] if isinstance(max_speed, list) else max_speed
    )  # take the first speed limit in case there are more
    try:
        max_speed = kmh_to_ms(float(max_speed))  # converting km/h to m/s
    except ValueError:
        logging.error(f"Max speed with value {max_speed} cannot be parsed as an int")
        max_speed = kmh_to_ms(50)  # default to 50 if parsing fails

    weight = length / max_speed

    new_distance: float = priority + weight
    return new_distance
