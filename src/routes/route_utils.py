import heapq as hq
import logging
from typing import Tuple

import geopandas as gpd
import networkx as nx
from shapely.geometry import Point

vertex = str
"""A tuple containing the latitude and longitude of a point"""

path = list[vertex]
"""A list of coordinates representing a route"""


def reconstruct_route(predecessor: dict[str, str | None], end: str) -> list[str]:
    path = []
    while end is not None:
        path.append(end)
        end = predecessor[end]  # type: ignore
    return path[::-1]


def is_in_dangerzone(
    v: vertex, danger_zone: gpd.GeoDataFrame, G: nx.MultiDiGraph
) -> bool:
    p = gpd.GeoSeries(
        data=[
            Point(G.nodes[v]["x"], G.nodes[v]["y"]),
        ],
        crs=danger_zone.crs,
    )
    return danger_zone.intersects(p)[0]  # type: ignore


def update_priority(
    heap: list[tuple[float, str]],
    node_priority: dict[str, float],
    node: str,
    new_priority: float,
) -> None:
    if new_priority < node_priority[node]:  # Only update if the new priority is better
        hq.heappush(heap, (new_priority, node))  # Push the new priority
        node_priority[node] = new_priority


def get_final_route(
    amount_of_routes: int,
    predecessor: dict[str, str | None],
    smallest_node: str,
    origin: str,
) -> Tuple[list[str], int]:
    """
    Returns the final route from the origin to the destination.

    :param amount_of_routes: The number of routes found.
    :param predecessor: A dictionary containing the predecessor of each node.
    :param smallest_node: The current node being processed.
    :param origin: The origin node.
    :return: The final route as a list of nodes.
    """
    amount_of_routes += 1
    result = reconstruct_route(predecessor, smallest_node)
    if result[0] != origin:
        logging.error("The first node in the route is not the origin node")
    return result, amount_of_routes
