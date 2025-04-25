import heapq as hq
import logging
from typing import Dict

import geopandas as gpd
import networkx as nx
import zope.interface
from tqdm import tqdm

from routes.route_algo import RouteAlgo
from routes.route_utils import (
    get_final_route,
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
        # has_path_been_calculated = dict((node, False) for node in origin_points)
        routes: dict[vertex, list[path]] = {}

        logging.info("Routing shortest path to safety for all origin points")

        for origin in tqdm(origin_points):
            amount_of_routes = 0
            # if has_path_been_calculated[origin]:
            #     continue  # path has already been calculated in another iteration
            if len(list(G.neighbors(origin))) == 0:
                logging.info(f"Node {origin} has no neighbors")
                continue  # Skip if the origin node doesn't have neighbors
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
                    final_route, amount_of_routes = get_final_route(
                        amount_of_routes=amount_of_routes,
                        predecessor=predecessor,
                        smallest_node=smallest_node,
                        origin=origin,
                    )
                    if final_route[0] in routes:
                        routes[final_route[0]].append(final_route)
                    else:
                        routes[final_route[0]] = [final_route]
                    if amount_of_routes >= diversifying_routes:
                        break  # there is no need to find other routes for this origin point
        return routes
