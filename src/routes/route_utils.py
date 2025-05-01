import heapq as hq
import logging
from typing import Callable, Dict, Tuple

import geopandas as gpd
import networkx as nx
from shapely.geometry import Point
from tqdm import tqdm

vertex = str
"""A tuple containing the latitude and longitude of a point"""

path = list[vertex]
"""A list of coordinates representing a route"""

RouteDict = dict[vertex, list[path]]


def route_to_safety_with_weight_func(
    origin_points: list[vertex],
    danger_zone: gpd.GeoDataFrame,
    G: nx.MultiDiGraph,
    weight_func: Callable,  # type: ignore
    diversifying_routes: int = 1,
) -> Dict[vertex, list[path]]:
    """
    Routes a list of origin points to the nearest safe location.

    :param origin_points: A list of vertices given as str IDs
    :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
    :param G: A graph corresponding to the road network
    :param weight_func: A function to calculate the weight of an edge.
    :param diversifying_routes: The number of routes to find for each origin point
    :return: A list of routes where each route corresponds to the origin point at the same index.
    """

    should_reuse_paths = diversifying_routes == 1
    has_path_been_calculated = dict((node, False) for node in origin_points)
    routes: dict[vertex, list[path]] = {}
    for origin in tqdm(origin_points):
        if has_path_been_calculated[origin] and should_reuse_paths:
            continue  # path has already been calculated in another iteration
        try:
            if len(list(G.neighbors(origin))) == 0:
                logging.info(f"Node {origin} has no neighbors")
                continue  # Skip if the origin node doesn't have neighbors
        except nx.NetworkXError:
            logging.error(f"Origin node {origin} is not in the graph")
            continue
        start, final_routes = _shortest_path_origin_point(
            origin=origin,
            G=G,
            danger_zone=danger_zone,
            diversifying_routes=diversifying_routes,
            weight_func=weight_func,
        )
        routes, has_path_been_calculated = handle_final_routes(
            routes=routes,
            has_path_been_calculated=has_path_been_calculated,
            origin=origin,
            final_routes=final_routes,
            should_reuse_paths=should_reuse_paths,
        )
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


def get_final_route(
    predecessor: dict[str, str | None],
    smallest_node: str,
    origin: str,
) -> list[str]:
    """
    Returns the final route from the origin to the destination.

    :param predecessor: A dictionary containing the predecessor of each node.
    :param smallest_node: The current node being processed.
    :param origin: The origin node.
    :return: The final route as a list of nodes.
    """
    result = reconstruct_route(predecessor, smallest_node)
    if result[0] != origin:
        logging.error("The first node in the route is not the origin node")
    return result


def handle_final_routes(
    routes: RouteDict,
    should_reuse_paths: bool,
    has_path_been_calculated: dict[str, bool],
    origin: str,
    final_routes: list[path],
) -> Tuple[RouteDict, dict[str, bool]]:
    routes[origin] = final_routes

    if should_reuse_paths and len(final_routes) > 1:
        # Only one route
        final_route = final_routes[0]
        has_path_been_calculated[origin] = True
        for i in range(
            len(final_route) - 1
        ):  # -1 since the last node is outside the danger zone and therefore does not need a path
            if (
                final_route[i] in has_path_been_calculated
                and not has_path_been_calculated[final_route[i]]
            ):
                routes[final_route[i]] = [final_route[i:]]
                # we take the route from i and forward
                has_path_been_calculated[final_route[i]] = True

    return routes, has_path_been_calculated


def _shortest_path_origin_point(
    origin: str,
    G: nx.MultiDiGraph,
    danger_zone: gpd.GeoDataFrame,
    diversifying_routes: int,
    weight_func: Callable,  # type: ignore
) -> Tuple[vertex, list[path]]:
    final_routes: list[path] = []
    sptSet = dict((node, False) for node in list(G.nodes))
    dist: list[tuple[float, str]] = [(float("inf"), node) for node in G.nodes]
    node_priority = {node: float("inf") for node in G.nodes}
    hq.heapify(dist)
    predecessor: dict[str, str | None] = {
        node: None for node in G.nodes
    }  # To track the shortest path

    update_priority(dist, node_priority, origin, 0)
    while dist:
        priority, smallest_node = hq.heappop(
            dist
        )  # popping the node with the current smallest dist to origin
        if priority == float("inf"):
            logging.info(f"Node {origin} cannot reach any nodes outside the dangerzone")
            break
        if (
            priority == node_priority[smallest_node]
        ):  # Only use values that are not outdated
            if not sptSet[smallest_node]:
                sptSet[smallest_node] = True
                for _, neighbour, edge_data in G.edges(
                    smallest_node, data=True
                ):  # looping through all adjacent vertices
                    new_distance = weight_func(priority=priority, edge_data=edge_data)

                    if is_in_dangerzone(smallest_node, danger_zone, G):
                        if new_distance < node_priority[neighbour]:
                            update_priority(
                                dist, node_priority, neighbour, new_distance
                            )
                            predecessor[neighbour] = smallest_node
        else:
            # This node has already been processed with a better path
            continue
        if not is_in_dangerzone(
            smallest_node, danger_zone, G
        ):  # We have found the shortest route to node outside danger zone
            final_route = get_final_route(
                predecessor=predecessor,
                smallest_node=smallest_node,
                origin=origin,
            )
            final_routes.append(final_route)

            if len(final_routes) >= diversifying_routes:
                return (
                    origin,
                    final_routes,
                )  # there is no need to find other routes for this origin point
    # If we have not found any routes, return the origin point as the only route
    return origin, final_routes
