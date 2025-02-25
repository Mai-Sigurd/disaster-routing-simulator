import heapq as hq
import logging

import geopandas as gpd
import networkx as nx
from tqdm import tqdm

from routes.route_utils import (
    is_in_dangerzone,
    path,
    reconstruct_route,
    update_priority,
    vertex,
)


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
    has_path_been_calculated = dict((node, False) for node in origin_points)
    routes = []

    logging.info("Routing shortest path to safety for all origin points")

    for origin in tqdm(origin_points):
        if has_path_been_calculated[origin]:
            continue  # path has already been calculated in another iteration
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
            priority, smallest_node = hq.heappop(
                dist
            )  # popping the node with the current smallest dist to origin
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
                    ):  # looping through all adjacent vertices
                        weight = edge_data.get("length", float("inf"))
                        # Default weight to inf, weight of edge between smallest_node and neighbour
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
                    logging.error("The first node in the route is not the origin node")
                routes.append(final_route)
                has_path_been_calculated[origin] = True
                for i in range(
                    len(final_route) - 1
                ):  # -1 since the last node is outside the dangerzone and therefore does not need a path
                    if (
                        final_route[i] in has_path_been_calculated
                        and not has_path_been_calculated[final_route[i]]
                    ):
                        routes.append(
                            final_route[i:]
                        )  # we take the route from i and forward
                        has_path_been_calculated[final_route[i]] = True

                break  # there is no need to find other routes for this origin point
    return routes
