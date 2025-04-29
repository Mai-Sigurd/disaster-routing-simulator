import heapq as hq
import logging
from typing import Dict, Tuple

import geopandas as gpd
import networkx as nx
import zope.interface
from tqdm import tqdm

from routes.route_algo import RouteAlgo
from routes.route_utils import (
    get_final_route,
    handle_final_routes,
    is_in_dangerzone,
    path,
    update_priority,
    vertex,
)


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
        should_reuse_paths = diversifying_routes == 1
        has_path_been_calculated = dict((node, False) for node in origin_points)
        routes: dict[vertex, list[path]] = {}

        logging.info("Routing shortest path to safety for all origin points")

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
                origin, G, danger_zone, diversifying_routes
            )
            routes, has_path_been_calculated = handle_final_routes(
                routes=routes,
                has_path_been_calculated=has_path_been_calculated,
                origin=origin,
                final_routes=final_routes,
                should_reuse_paths=should_reuse_paths,
            )
        return routes


def _shortest_path_origin_point(
    origin: str,
    G: nx.MultiDiGraph,
    danger_zone: gpd.GeoDataFrame,
    diversifying_routes: int,
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
                    weight = edge_data.get("length", float("inf"))
                    # Default weight to inf, weight of edge between smallest_node and neighbour
                    new_distance = priority + weight

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
