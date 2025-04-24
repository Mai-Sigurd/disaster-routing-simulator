from typing import Dict

import geopandas as gpd
import networkx as nx
import zope.interface

from routes.route_utils import path, vertex


class RouteAlgo(zope.interface.Interface):  # type: ignore[misc]
    title = zope.interface.Attribute(
        "Title of the routing algorithm used in the SimWrapper dashboard and the MATSim output directory."
    )

    def route_to_safety(
        self,
        origin_points: list[vertex],
        danger_zone: gpd.GeoDataFrame,
        G: nx.MultiDiGraph,
        diversifying_routes: int = 3,
    ) -> Dict[vertex, list[path]]:
        """
        Finds a list of paths from origin points to a safe location.

        :param origin_points: A list of vertices given as str IDs
        :param danger_zone: A GeoDataFrame containing the danger zone polygon(s).
        :param G: A graph corresponding to the road network
        :param diversifying_routes: The number of routes to find for each origin point
        :return: A dictionary from an origin point to a list of 1 or more paths .
        """
        raise NotImplementedError(
            "The route_to_safety method must be implemented in the subclass."
        )
