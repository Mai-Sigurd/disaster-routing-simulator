import heapq as hq
import logging

import geopandas as gpd
import networkx as nx
from shapely.geometry import Point
from tqdm import tqdm

vertex = str
"""A tuple containing the latitude and longitude of a point"""

path = list[vertex]
"""A list of coordinates representing a route"""


# based on: https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/
def route_to_safety(
    origin_points: list[vertex], danger_zone: gpd.GeoDataFrame, G: nx.MultiDiGraph
) -> list[path]:
    """
    Routes a list of origin points to the nearest safe location.

    :param origin_points: A list of vertices given as str IDs
    :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
    :param G: A graph corresponding to the road network
    :return: A list of routes where each route corresponds to the origin point at the same index.
    """
    logging.info("Routing shortest path to safety for all origin points")
    routes = []

    for origin in tqdm(origin_points):
        if len(list(G.neighbors(origin))) == 0:
            logging.info(f"Node {origin} has no neighbors")
            continue  # Skip if the origin node doesn't have neighbors
        sptSet = dict((node, False) for node in list(G.nodes))
        dist: list[tuple[float, str]] = [(float("inf"), node) for node in G.nodes]
        node_priority = {node: float("inf") for node in G.nodes}
        hq.heapify(dist)
        predecessor: dict[str, str | None] = {
            node: None for node in G.nodes
        }  # To track shortest path

        update_priority(dist, node_priority, origin, 0)
        while dist:
            priority, smallest_node = hq.heappop(dist)
            if priority == float("inf"):
                logging.info(
                    f"Node {origin} cannot reach any nodes outside the dangerzone"
                )
                break
            if (
                priority == node_priority[smallest_node]
            ):  # Only use values that are not outdated
                if not sptSet[smallest_node]:
                    sptSet[smallest_node] = True
                    for _, neighbour, edge_data in G.edges(
                        smallest_node, data=True
                    ):  # Multiple edges between two nodes possible
                        weight = edge_data.get("length", float("inf"))
                        # Default weight to inf, weight of edge between popped_node and neighbour
                        new_distance = priority + weight

                        if new_distance < node_priority[neighbour]:
                            update_priority(
                                dist, node_priority, neighbour, new_distance
                            )
                            predecessor[neighbour] = smallest_node

            if not is_in_dangerzone(
                smallest_node, danger_zone, G
            ):  # We have found shortest route to node outside dangerzone
                final_route = reconstruct_route(predecessor, smallest_node)
                if final_route[0] != origin:
                    raise Exception(
                        "The first node in the route is not the origin node"
                    )
                routes.append(final_route)
                break  # there is no need to find other routes
    return routes


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
